"""
repositories/mongo/proveedores_repo.py
=======================================
Repositorio documental para proveedores (MongoDB).
"""
from typing import List, Optional, Dict
from database import MongoDB

class ProveedoresRepository:
    def __init__(self, db: MongoDB):
        self._db = db

    def get_all(self) -> List[Dict]:
        return self._db.get_all_proveedores()

    def get_by_codigo(self, codigo: str) -> Optional[Dict]:
        return self._db.get_proveedor(codigo)

    def create(self, codigo: str, nombre_empresa: str, lineas_productos: list,
               telefono: str, email: str) -> Dict:
        return self._db.create_proveedor(codigo, nombre_empresa, lineas_productos, telefono, email)

    def update(self, codigo: str, nombre_empresa: str, lineas_productos: list,
               telefono: str, email: str) -> bool:
        return self._db.update_proveedor(codigo, nombre_empresa, lineas_productos, telefono, email)
