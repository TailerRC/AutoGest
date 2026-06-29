"""
repositories/oracle/repuestos_repo.py
======================================
Repositorio para INVENTARIO_REPUESTOS (Oracle).
"""
from typing import List, Optional, Dict
from database import OracleDB


class RepuestoRepository:
    """
    Repositorio de repuestos/inventario conectado a base de datos Oracle.
    """

    def __init__(self, db: OracleDB):
        self._db = db

    def get_all(self) -> List[Dict]:
        """
        Obtiene la lista completa de repuestos.
        INTEGRACIÓN: Usado en la cotización de repuestos de servicio (MongoDB) y
        en la facturación del taller.
        """
        return self._db.get_all_repuestos()

    def get_by_id(self, id_pieza: int) -> Optional[Dict]:
        """
        Busca un repuesto por su ID interno secuencial.
        INTEGRACIÓN: Referenciado por DETALLE_ORDEN_REPUESTOS en la BD Oracle.
        """
        return self._db.get_repuesto(id_pieza)

    def get_criticos(self, umbral: int = 2) -> List[Dict]:
        """
        Retorna repuestos con stock <= umbral para alertas de sistema.
        INTEGRACIÓN: Alimenta el panel principal de alertas de stock crítico.
        """
        return [r for r in self._db.get_all_repuestos() if r["stock"] <= umbral]

    def create(self, codigo: str, nombre: str, stock: int,
               precio_venta: float, proveedor: str) -> Dict:
        """
        Registra un nuevo repuesto en la tabla INVENTARIO_REPUESTOS.
        """
        return self._db.create_repuesto(codigo, nombre, stock, precio_venta, proveedor)

    def update(self, id_pieza: int, codigo: str, nombre: str,
               stock: int, precio_venta: float, proveedor: str) -> bool:
        """
        Actualiza los datos físicos de un repuesto.
        INTEGRACIÓN: Al actualizar el stock, se recalculan alertas y proformas.
        """
        return self._db.update_repuesto(id_pieza, codigo, nombre, stock, precio_venta, proveedor)

    def tiene_dependencias(self, id_pieza: int) -> bool:
        """
        Verifica si el repuesto está asociado a algún detalle de orden de trabajo.
        """
        conn = self._db._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM DETALLE_ORDEN_REPUESTOS WHERE id_pieza = :1", [id_pieza])
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count > 0

    def delete(self, id_pieza: int) -> bool:
        """
        Elimina un repuesto del catálogo.
        INTEGRACIÓN: Antes de eliminar, verificar que el id_pieza no esté referenciado 
        en DETALLE_ORDEN_REPUESTOS para evitar errores de integridad referencial (FK constraint).
        """
        return self._db.delete_repuesto(id_pieza)

