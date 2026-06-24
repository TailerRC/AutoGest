"""
services/facturas_svc.py
=========================
Lógica de negocio para Facturas.
"""
from typing import List, Optional, Dict
from repositories.oracle.facturas_repo import FacturaRepository
from repositories.oracle.ordenes_repo  import OrdenRepository


class FacturaService:
    """
    Servicio de Facturas — reglas de negocio puras.
    """

    ESTADOS_PAGO_VALIDOS  = {"pendiente", "pagada"}
    METODOS_PAGO_VALIDOS  = {"Efectivo", "Tarjeta Débito", "Tarjeta Crédito", "Transferencia"}

    def __init__(self, repo: FacturaRepository, orden_repo: OrdenRepository):
        self._repo      = repo
        self._orden_repo = orden_repo

    def listar(self) -> List[Dict]:
        return self._repo.get_all()

    def obtener(self, id_factura: int) -> Optional[Dict]:
        return self._repo.get_by_id(id_factura)

    def obtener_por_orden(self, id_orden: int) -> Optional[Dict]:
        return self._repo.get_by_orden(id_orden)

    def crear(self, id_orden: int, total: float, metodo_pago: str) -> Dict:
        """
        Reglas de negocio:
          - La orden debe existir.
          - Una orden solo puede tener una factura.
          - El método de pago debe ser válido.
        """
        if not self._orden_repo.get_by_id(id_orden):
            raise ValueError(f"La orden #{id_orden} no existe.")
        if self._repo.get_by_orden(id_orden):
            raise ValueError(f"La orden #{id_orden} ya tiene una factura registrada.")
        if metodo_pago not in self.METODOS_PAGO_VALIDOS:
            raise ValueError(f"Método de pago inválido: {metodo_pago}")
        return self._repo.create(id_orden, total, metodo_pago)

    def cambiar_estado(self, id_factura: int, estado_pago: str) -> bool:
        if estado_pago not in self.ESTADOS_PAGO_VALIDOS:
            raise ValueError(f"Estado de pago inválido: {estado_pago}")
        return self._repo.update_estado(id_factura, estado_pago)
