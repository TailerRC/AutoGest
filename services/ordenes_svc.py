"""
services/ordenes_svc.py
========================
Lógica de negocio para Órdenes de Trabajo.
Incluye reglas de orquestación entre Oracle y la capa de stock.
"""
import re
from typing import List, Optional, Dict
from repositories.oracle.ordenes_repo   import OrdenRepository
from repositories.oracle.repuestos_repo import RepuestoRepository


class OrdenService:
    """
    Servicio de Órdenes de Trabajo — reglas de negocio puras.
    """

    ESTADOS_VALIDOS = {"pendiente", "en_proceso", "completada", "cancelada"}

    def __init__(self, repo: OrdenRepository, repuesto_repo: RepuestoRepository):
        self._repo         = repo
        self._repuesto_repo = repuesto_repo

    def listar(self) -> List[Dict]:
        return self._repo.get_all()

    def obtener(self, id_orden: int) -> Optional[Dict]:
        return self._repo.get_by_id(id_orden)

    def obtener_detallada(self, id_orden: int) -> Optional[Dict]:
        return self._repo.get_detallada(id_orden)

    def crear(self, id_vehiculo: int, id_empleado: int,
              fecha_ingreso: str, fecha_entrega: str) -> Dict:
        """
        Reglas de negocio:
          - Estado inicial siempre es 'pendiente'.
          - Fechas son strings YYYY-MM-DD.
        """
        return self._repo.create(id_vehiculo, id_empleado, fecha_ingreso, fecha_entrega)

    def actualizar(self, id_orden: int, id_vehiculo: int, id_empleado: int,
                   fecha_ingreso: str, fecha_entrega: str, estado: str) -> bool:
        if estado not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido: {estado}")
        return self._repo.update(id_orden, id_vehiculo, id_empleado,
                                  fecha_ingreso, fecha_entrega, estado)

    def cambiar_estado(self, id_orden: int, estado: str) -> bool:
        """
        Cambia solo el estado de una orden.
        Regla de negocio: no se puede reabrir una orden cancelada.
        """
        if estado not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido: {estado}")
        orden = self._repo.get_by_id(id_orden)
        if not orden:
            return False
        return self._repo.update_estado(id_orden, estado)

    def agregar_repuesto(self, id_orden: int, id_pieza: int,
                         cantidad: int, precio_unitario: float) -> Dict:
        """
        Agrega un repuesto a la orden.
        Regla de negocio: verifica que haya stock suficiente.
        """
        repuesto = self._repuesto_repo.get_by_id(id_pieza)
        if not repuesto:
            raise ValueError(f"El repuesto #{id_pieza} no existe.")
        if repuesto["stock"] < cantidad:
            raise ValueError(
                f"Stock insuficiente. Disponible: {repuesto['stock']}, solicitado: {cantidad}."
            )
        return self._repo.add_detalle(id_orden, id_pieza, cantidad, precio_unitario)

    def get_stats_estados(self, ordenes: List[Dict]) -> Dict[str, int]:
        """Genera resumen de cantidades por estado."""
        stats = {"pendiente": 0, "en_proceso": 0, "completada": 0, "cancelada": 0}
        for o in ordenes:
            estado = o.get("estado", "pendiente")
            if estado in stats:
                stats[estado] += 1
        return stats

    def _normalizar(self, texto: str) -> str:
        """trim + lowercase + colapsar espacios múltiples."""
        return re.sub(r"\s+", " ", (texto or "").strip().lower())

    def cargar_cotizacion(self, id_orden: int, cotizacion: Dict, repuestos_inventario: List[Dict]) -> Dict:
        """
        Procesa una cotización de Mongo y la aplica a una orden existente:
          - Cada línea {item, precio} se clasifica contra el inventario por nombre normalizado.
          - Si coincide -> es repuesto: cantidad = round(precio / precio_venta_actual),
            se inserta en DETALLE_ORDEN_REPUESTOS (vía agregar_repuesto, que ya valida stock
            y descuenta inventario).
          - Si no coincide -> es servicio: queda solo informativo, no se persiste en Oracle.

        Retorna un resumen para mostrar en pantalla:
          {
            "repuestos_cargados": [{"nombre","cantidad","precio_unitario","subtotal"}],
            "servicios": [{"item","precio"}],
            "advertencias": ["mensaje..."],
            "total_repuestos": float,
            "total_servicios": float,
            "total_general": float,
          }
        """
        indice_inventario = {
            self._normalizar(r["nombre"]): r for r in repuestos_inventario
        }

        repuestos_cargados = []
        servicios = []
        advertencias = []

        for linea in cotizacion.get("servicios_repuestos", []):
            item = linea.get("item", "")
            precio = float(linea.get("precio", 0.0))
            clave = self._normalizar(item)

            repuesto = indice_inventario.get(clave)
            if repuesto is None:
                # No coincide con inventario -> es un servicio (mano de obra)
                servicios.append({"item": item, "precio": precio})
                continue

            precio_venta = float(repuesto.get("precio_venta", 0.0))
            if precio_venta <= 0:
                advertencias.append(
                    f"'{item}' coincide con el inventario pero no tiene precio de venta válido; se omitió."
                )
                continue

            cantidad_exacta = precio / precio_venta
            cantidad = max(1, round(cantidad_exacta))

            # Advertencia si el redondeo se aleja de forma notoria del valor exacto
            diferencia = abs(cantidad_exacta - cantidad)
            if diferencia > 0.15:
                advertencias.append(
                    f"'{item}': el precio cotizado (S/. {precio:.2f}) no coincide exactamente "
                    f"con {cantidad} unidad(es) al precio actual (S/. {precio_venta:.2f} c/u). "
                    f"Verifica antes de confirmar."
                )

            try:
                self.agregar_repuesto(id_orden, repuesto["id_pieza"], cantidad, precio_venta)
                repuestos_cargados.append({
                    "nombre": repuesto["nombre"],
                    "cantidad": cantidad,
                    "precio_unitario": precio_venta,
                    "subtotal": cantidad * precio_venta,
                })
            except ValueError as e:
                advertencias.append(f"'{item}': no se pudo cargar — {str(e)}")

        total_repuestos = sum(r["subtotal"] for r in repuestos_cargados)
        total_servicios = sum(s["precio"] for s in servicios)

        return {
            "repuestos_cargados": repuestos_cargados,
            "servicios": servicios,
            "advertencias": advertencias,
            "total_repuestos": total_repuestos,
            "total_servicios": total_servicios,
            "total_general": total_repuestos + total_servicios,
        }
    
    def clasificar_cotizacion(self, cotizacion: Dict, repuestos_inventario: List[Dict]) -> Dict:
        """
        Igual que cargar_cotizacion pero SOLO LECTURA: clasifica servicios vs repuestos
        para mostrar en pantalla, sin insertar nada en Oracle ni descontar stock.
        """
        indice_inventario = {
            self._normalizar(r["nombre"]): r for r in repuestos_inventario
        }

        repuestos_cotizados = []
        servicios = []

        for linea in cotizacion.get("servicios_repuestos", []):
            item = linea.get("item", "")
            precio = float(linea.get("precio", 0.0))
            clave = self._normalizar(item)

            repuesto = indice_inventario.get(clave)
            if repuesto is None:
                servicios.append({"item": item, "precio": precio})
            else:
                repuestos_cotizados.append({"item": item, "precio": precio})

        total_servicios = sum(s["precio"] for s in servicios)
        total_repuestos_cotizados = sum(r["precio"] for r in repuestos_cotizados)

        return {
            "servicios": servicios,
            "repuestos_cotizados": repuestos_cotizados,
            "total_servicios": total_servicios,
            "total_repuestos_cotizados": total_repuestos_cotizados,
            "total_general": total_servicios + total_repuestos_cotizados,
        }
    
    def quitar_repuesto(self, id_detalle: int) -> bool:
        """
        Elimina un repuesto de la orden y repone esa cantidad al stock
        (vía OrdenRepository.eliminar_detalle, que ya hace el UPDATE de stock).
        """
        return self._repo.eliminar_detalle(id_detalle)