"""
repositories/mongo/historial_repo.py
=====================================
Repositorio documental para historial_mantenimiento_vehiculo (MongoDB).
"""
from typing import List, Optional, Dict, Any
from database import MongoDB

class HistorialRepository:
    """
    Repositorio de acceso a datos para el historial de mantenimiento en MongoDB.
    """
    def __init__(self, db: MongoDB):
        self._db = db

    def get_all(self) -> List[Dict]:
        """Consulta y retorna todos los registros de historial de la base de datos."""
        return self._db.get_all_historial()

    def get_by_vehiculo(self, id_vehiculo: int) -> Optional[Dict]:
        """Obtiene la bitácora de historial específica para un id de vehículo."""
        return self._db.get_historial_by_vehiculo(id_vehiculo)

    def create(self, id_vehiculo: int, kilometraje_ingreso: int,
               fecha_servicio: Any, estado_final: str,
               diagnosticos_asociados: list = None) -> Dict:
        """Registra un nuevo evento de mantenimiento en MongoDB."""
        return self._db.create_historial(
            id_vehiculo, kilometraje_ingreso, fecha_servicio,
            estado_final, diagnosticos_asociados
        )
