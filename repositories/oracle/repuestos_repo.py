"""
repositories/oracle/repuestos_repo.py
======================================
Repositorio para INVENTARIO_REPUESTOS (Oracle).
"""
from typing import List, Optional, Dict
from database import OracleDB


class RepuestoRepository:
    """
    Repositorio de repuestos/inventario.

    TODO (Oracle real): reemplazar por queries con cx_Oracle
    """

    def __init__(self, db: OracleDB):
        self._db = db

    def get_all(self) -> List[Dict]:
        """
        TODO: SELECT * FROM INVENTARIO_REPUESTOS ORDER BY nombre
        """
        return self._db.get_all_repuestos()

    def get_by_id(self, id_pieza: int) -> Optional[Dict]:
        """
        TODO: SELECT * FROM INVENTARIO_REPUESTOS WHERE id_pieza=:1
        """
        return self._db.get_repuesto(id_pieza)

    def get_criticos(self, umbral: int = 2) -> List[Dict]:
        """
        Retorna repuestos con stock <= umbral.
        TODO: SELECT * FROM INVENTARIO_REPUESTOS WHERE stock <= :umbral
        """
        return [r for r in self._db.get_all_repuestos() if r["stock"] <= umbral]

    def create(self, codigo: str, nombre: str, stock: int,
               precio_venta: float, proveedor: str) -> Dict:
        """
        TODO: INSERT INTO INVENTARIO_REPUESTOS VALUES(SEQ_REP.NEXTVAL,:1,:2,:3,:4,:5)
        """
        return self._db.create_repuesto(codigo, nombre, stock, precio_venta, proveedor)

    def update(self, id_pieza: int, codigo: str, nombre: str,
               stock: int, precio_venta: float, proveedor: str) -> bool:
        """
        TODO: UPDATE INVENTARIO_REPUESTOS SET ... WHERE id_pieza=:1
        """
        return self._db.update_repuesto(id_pieza, codigo, nombre, stock, precio_venta, proveedor)

    def delete(self, id_pieza: int) -> bool:
        """
        TODO: DELETE FROM INVENTARIO_REPUESTOS WHERE id_pieza=:1
        """
        return self._db.delete_repuesto(id_pieza)
