"""
repositories/mongo/historial_repo.py
=====================================
Repositorio documental para historial_mantenimiento_vehiculo (MongoDB).
"""
from typing import List, Optional, Dict
from database import MongoDB

class HistorialRepository:
    def __init__(self, db: MongoDB):
        self._db = db

    def get_all(self) -> List[Dict]:
        return self._db.get_all_historial()

    def get_by_vehiculo(self, id_vehiculo: int) -> Optional[Dict]:
        return self._db.get_historial_by_vehiculo(id_vehiculo)

    def create(self, id_vehiculo: int, kilometraje_ingreso: int,
               fecha_servicio: str, estado_final: str,
               diagnosticos_asociados: list = None) -> Dict:
        return self._db.create_historial(
            id_vehiculo, kilometraje_ingreso, fecha_servicio,
            estado_final, diagnosticos_asociados
        )
