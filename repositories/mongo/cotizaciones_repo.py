"""
repositories/mongo/cotizaciones_repo.py
========================================
Repositorio documental para cotizaciones (MongoDB).
"""
from typing import List, Optional, Dict
from database import MongoDB

class CotizacionesRepository:
    def __init__(self, db: MongoDB):
        self._db = db

    def get_all(self) -> List[Dict]:
        return self._db.get_all_cotizaciones()

    def get_by_codigo(self, codigo: str) -> Optional[Dict]:
        return self._db.get_cotizacion(codigo)

    def create(self, codigo: str, id_cliente: int, id_vehiculo: int,
               fecha_validez: str, servicios: list, total: float) -> Dict:
        return self._db.create_cotizacion(
            codigo, id_cliente, id_vehiculo, fecha_validez, servicios, total
        )
