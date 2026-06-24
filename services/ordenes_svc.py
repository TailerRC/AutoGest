"""
services/ordenes_svc.py
========================
Lógica de negocio para Órdenes de Trabajo.
Incluye reglas de orquestación entre Oracle y la capa de stock.
"""
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
