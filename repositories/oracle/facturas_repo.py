"""
repositories/oracle/facturas_repo.py
=====================================
Repositorio para la tabla FACTURAS (Oracle).
"""
from typing import List, Optional, Dict
from database import OracleDB


class FacturaRepository:
    """
    Repositorio de facturas.

    TODO (Oracle real): reemplazar por queries con cx_Oracle
    """

    def __init__(self, db: OracleDB):
        self._db = db

    def get_all(self) -> List[Dict]:
        """
        Facturas enriquecidas con nombre_cliente y placa.
        TODO: SELECT f.*, c.nombre, v.placa
              FROM FACTURAS f
              JOIN ORDENES_TRABAJO o ON f.id_orden=o.id_orden
              JOIN VEHICULOS v ON o.id_vehiculo=v.id_vehiculo
              JOIN CLIENTES  c ON v.id_cliente=c.id_cliente
        """
        return self._db.get_all_facturas()

    def get_by_id(self, id_factura: int) -> Optional[Dict]:
        """
        TODO: SELECT * FROM FACTURAS WHERE id_factura=:1
        """
        return self._db.get_factura(id_factura)

    def get_by_orden(self, id_orden: int) -> Optional[Dict]:
        """
        TODO: SELECT * FROM FACTURAS WHERE id_orden=:1
        """
        return self._db.get_factura_por_orden(id_orden)

    def create(self, id_orden: int, total: float, metodo_pago: str) -> Dict:
        """
        TODO: INSERT INTO FACTURAS VALUES(SEQ_FAC.NEXTVAL,:1,SYSDATE,:2,:3,'pendiente')
        """
        return self._db.create_factura(id_orden, total, metodo_pago)

    def update_estado(self, id_factura: int, estado_pago: str) -> bool:
        """
        TODO: UPDATE FACTURAS SET estado_pago=:1 WHERE id_factura=:2
        """
        return self._db.update_factura_estado(id_factura, estado_pago)
