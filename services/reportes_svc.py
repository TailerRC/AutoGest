"""
services/reportes_svc.py
=========================
Lógica de negocio para Reportes Combinados Oracle + MongoDB.
Orquesta múltiples repositorios para generar vistas integradas.
"""
from typing import List, Optional, Dict
from repositories.oracle.ordenes_repo  import OrdenRepository
from repositories.oracle.facturas_repo import FacturaRepository
from repositories.oracle.repuestos_repo import RepuestoRepository
from repositories.mongo.bitacora_repo  import BitacoraRepository
from repositories.mongo.catalogo_repo  import CatalogoRepository
from repositories.mongo.logs_repo      import LogsRepository


class ReporteService:
    """
    Servicio de Reportes — agrega datos de Oracle y MongoDB.
    """

    def __init__(
        self,
        orden_repo:    OrdenRepository,
        factura_repo:  FacturaRepository,
        repuesto_repo: RepuestoRepository,
        bitacora_repo: BitacoraRepository,
        catalogo_repo: CatalogoRepository,
        logs_repo:     LogsRepository,
    ):
        self._ordenes   = orden_repo
        self._facturas  = factura_repo
        self._repuestos = repuesto_repo
        self._bitacora  = bitacora_repo
        self._catalogo  = catalogo_repo
        self._logs      = logs_repo

    def resumen_general(self) -> Dict:
        """
        Estadísticas de alto nivel para la pantalla de reportes.
        Combina datos de Oracle y MongoDB.
        """
        ordenes  = self._ordenes.get_all()
        facturas = self._facturas.get_all()
        bitacoras = self._bitacora.get_all()
        alertas  = self._logs.get_alertas_activas()

        return {
            "total_ordenes":  len(ordenes),
            "total_facturas": len(facturas),
            "total_bitacoras": len(bitacoras),
            "alertas_activas": len(alertas),
        }

    def reporte_por_orden(self, id_orden: int) -> Optional[Dict]:
        """
        Genera el reporte completo de una orden:
        - Datos Oracle: orden, cliente, vehículo, empleado, repuestos, factura
        - Datos MongoDB: bitácora de diagnóstico, especificaciones técnicas
        """
        orden = self._ordenes.get_detallada(id_orden)
        if not orden:
            return None

        vehiculo = orden.get("vehiculo") or {}
        id_vehiculo = vehiculo.get("id_vehiculo")

        factura  = self._facturas.get_by_orden(id_orden)
        bitacora = self._bitacora.get_by_vehiculo(id_vehiculo) if id_vehiculo else None

        # Buscar especificaciones técnicas del vehículo en MongoDB
        catalogo = self._catalogo.buscar(
            marca=vehiculo.get("marca", ""),
            modelo=vehiculo.get("modelo", ""),
            año=vehiculo.get("año"),
        )
        esp_tecnica = catalogo[0] if catalogo else None

        detalles   = orden.get("detalles", [])
        total_rep  = sum(d.get("subtotal", 0) for d in detalles)
        mano_obra  = 0  # El nuevo mock de MongoDB ya no tiene el campo mano_de_obra

        return {
            "orden":       orden,
            "cliente":     orden.get("cliente") or {},
            "vehiculo":    vehiculo,
            "empleado":    orden.get("empleado") or {},
            "detalles":    detalles,
            "factura":     factura,
            "bitacora":    bitacora,
            "esp_tecnica": esp_tecnica,
            "total_rep":   total_rep,
            "mano_obra":   mano_obra,
            "gran_total":  total_rep + mano_obra,
        }

    def get_logs_recientes(self, limit: int = 10) -> List[Dict]:
        return self._logs.get_recent(limit=limit)

    def get_ordenes_lista(self) -> List[Dict]:
        return self._ordenes.get_all()
