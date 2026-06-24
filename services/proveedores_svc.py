"""
services/proveedores_svc.py
===========================
Lógica de negocio para los Proveedores (MongoDB).
"""
from typing import List, Optional, Dict
from repositories.mongo.proveedores_repo import ProveedoresRepository

class ProveedoresService:
    def __init__(self, repo: ProveedoresRepository):
        self._repo = repo

    def listar(self) -> List[Dict]:
        return self._repo.get_all()

    def obtener_por_codigo(self, codigo: str) -> Optional[Dict]:
        return self._repo.get_by_codigo(codigo)
