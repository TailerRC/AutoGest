"""
repositories/oracle/ordenes_repo.py
=====================================
Repositorio para ORDENES_TRABAJO y DETALLE_ORDEN_REPUESTOS (Oracle).
"""
from typing import List, Optional, Dict
from database import OracleDB


class OrdenRepository:
    """
    Repositorio de órdenes de trabajo + detalles de repuestos.

    TODO (Oracle real): reemplazar por queries con cx_Oracle
    """

    def __init__(self, db: OracleDB):
        self._db = db

    # ── Órdenes ───────────────────────────────────────────────────────

    def get_all(self) -> List[Dict]:
        """
        Órdenes enriquecidas con placa, cliente y empleado.
        TODO: SELECT o.*, v.placa, c.nombre, e.nombre
              FROM ORDENES_TRABAJO o
              JOIN VEHICULOS v ON o.id_vehiculo=v.id_vehiculo
              JOIN CLIENTES  c ON v.id_cliente=c.id_cliente
              JOIN EMPLEADOS e ON o.id_empleado=e.id_empleado
        """
        return self._db.get_all_ordenes()

    def get_by_id(self, id_orden: int) -> Optional[Dict]:
        """
        TODO: SELECT * FROM ORDENES_TRABAJO WHERE id_orden=:1
        """
        return self._db.get_orden(id_orden)

    def get_detallada(self, id_orden: int) -> Optional[Dict]:
        """
        Orden con vehiculo, cliente, empleado y detalles de repuestos.
        """
        return self._db.get_orden_detallada(id_orden)

    def create(self, id_vehiculo: int, id_empleado: int,
               fecha_ingreso: str, fecha_entrega: str) -> Dict:
        """
        TODO: INSERT INTO ORDENES_TRABAJO VALUES(SEQ_ORD.NEXTVAL,:1,:2,:3,:4,'pendiente')
        """
        return self._db.create_orden(id_vehiculo, id_empleado, fecha_ingreso, fecha_entrega)

    def update(self, id_orden: int, id_vehiculo: int, id_empleado: int,
               fecha_ingreso: str, fecha_entrega: str, estado: str) -> bool:
        """
        TODO: UPDATE ORDENES_TRABAJO SET ... WHERE id_orden=:1
        """
        return self._db.update_orden(id_orden, id_vehiculo, id_empleado,
                                     fecha_ingreso, fecha_entrega, estado)

    def update_estado(self, id_orden: int, estado: str) -> bool:
        """
        TODO: UPDATE ORDENES_TRABAJO SET estado=:1 WHERE id_orden=:2
        """
        return self._db.update_orden_estado(id_orden, estado)

    # ── Detalles de repuestos ─────────────────────────────────────────

    def get_detalles(self, id_orden: int) -> List[Dict]:
        """
        TODO: SELECT d.*, p.nombre FROM DETALLE_ORDEN_REPUESTOS d
              JOIN INVENTARIO_REPUESTOS p ON d.id_pieza=p.id_pieza
              WHERE d.id_orden=:1
        """
        return self._db.get_detalles_orden(id_orden)

    def add_detalle(self, id_orden: int, id_pieza: int,
                    cantidad: int, precio_unitario: float) -> Dict:
        """
        Agrega repuesto a la orden y descuenta stock automáticamente.
        TODO: INSERT INTO DETALLE_ORDEN_REPUESTOS ...
              UPDATE INVENTARIO_REPUESTOS SET stock=stock-:cantidad WHERE id_pieza=:id_pieza
        """
        return self._db.add_detalle_orden(id_orden, id_pieza, cantidad, precio_unitario)
