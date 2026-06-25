"""
services/historial_svc.py
=========================
Lógica de negocio para el Historial de Mantenimiento (MongoDB).
"""
from typing import List, Optional, Dict
from datetime import date
from repositories.mongo.historial_repo import HistorialRepository
from repositories.oracle.vehiculos_repo import VehiculoRepository


class HistorialService:
    def __init__(self, repo: HistorialRepository, veh_repo: VehiculoRepository):
        self._repo = repo
        self._veh_repo = veh_repo

    def listar(self) -> List[Dict]:
        return self._repo.get_all()

    def obtener_por_vehiculo(self, id_vehiculo: int) -> Optional[Dict]:
        return self._repo.get_by_vehiculo(id_vehiculo)

    def crear(self, id_vehiculo: int, kilometraje_ingreso: int,
              fecha_servicio: str, estado_final: str) -> Dict:
        return self._repo.create(
            id_vehiculo, kilometraje_ingreso, fecha_servicio, estado_final
        )
