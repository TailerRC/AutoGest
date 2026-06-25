"""
services/cotizaciones_svc.py
============================
Lógica de negocio para las Cotizaciones (MongoDB).
"""
import uuid
from typing import List, Optional, Dict
from datetime import date
from repositories.mongo.cotizaciones_repo import CotizacionesRepository


class CotizacionesService:
    def __init__(self, repo: CotizacionesRepository):
        self._repo = repo

    def listar(self) -> List[Dict]:
        return self._repo.get_all()

    def obtener_por_codigo(self, codigo: str) -> Optional[Dict]:
        return self._repo.get_by_codigo(codigo)

    def crear(self, id_cliente: int, id_vehiculo: int,
              fecha_validez: str, servicios: list, total: float) -> Dict:
        codigo = f"COT-{uuid.uuid4().hex[:6].upper()}"
        return self._repo.create(codigo, id_cliente, id_vehiculo,
                                 fecha_validez, servicios, total)
