"""
repositories/mongo/proveedores_repo.py
=======================================
Repositorio documental para proveedores (MongoDB).
"""
from typing import List, Optional, Dict
from database import MongoDB

class ProveedoresRepository:
    """
    Repositorio para la colección de proveedores en MongoDB.
    """
    def __init__(self, db: MongoDB):
        self._db = db

    def get_all(self) -> List[Dict]:
        """Obtiene la lista completa de todos los proveedores."""
        return self._db.get_all_proveedores()

    def get_by_codigo(self, codigo: str) -> Optional[Dict]:
        """Busca un proveedor específico por su código único."""
        return self._db.get_proveedor(codigo)

    def get_ultimo_codigo(self, prefix: str = "PROV-") -> Optional[str]:
        """
        Obtiene el último código de proveedor registrado en MongoDB.
        Ordena descendentemente para encontrar el correlativo más alto.
        """
        doc = self._db.proveedores.find_one(
            {"codigoProveedor": {"$regex": f"^{prefix}"}},
            sort=[("codigoProveedor", -1)]
        )
        return doc.get("codigoProveedor") if doc else None

    def create(self, codigo: str, nombre_empresa: str, lineas_productos: list,
               telefono: str, email: str) -> Dict:
        """Registra un nuevo proveedor en la base de datos."""
        return self._db.create_proveedor(codigo, nombre_empresa, lineas_productos, telefono, email)

    def update(self, codigo: str, nombre_empresa: str, lineas_productos: list,
               telefono: str, email: str) -> bool:
        """Actualiza la información de un proveedor existente."""
        return self._db.update_proveedor(codigo, nombre_empresa, lineas_productos, telefono, email)

