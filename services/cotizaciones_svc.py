"""
services/cotizaciones_svc.py
============================
Lógica de negocio para las Cotizaciones (MongoDB).
"""
from typing import List, Optional, Dict
from repositories.mongo.cotizaciones_repo import CotizacionesRepository

class CotizacionesService:
    def __init__(self, repo: CotizacionesRepository):
        self._repo = repo

    def listar(self) -> List[Dict]:
        return self._repo.get_all()

    def obtener_por_codigo(self, codigo: str) -> Optional[Dict]:
        return self._repo.get_by_codigo(codigo)
