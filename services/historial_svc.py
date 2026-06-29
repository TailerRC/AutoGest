"""
services/historial_svc.py
=========================
Lógica de negocio para el Historial de Mantenimiento (MongoDB).
"""
from typing import List, Optional, Dict
from datetime import date
from repositories.mongo.historial_repo import HistorialRepository
from repositories.oracle.vehiculos_repo import VehiculoRepository


from datetime import datetime

class HistorialService:
    """
    Servicio de negocio para gestionar el historial de mantenimiento de vehículos.
    """
    def __init__(self, repo: HistorialRepository, veh_repo: VehiculoRepository):
        self._repo = repo
        self._veh_repo = veh_repo

    def listar(self) -> List[Dict]:
        """Obtiene todos los registros del historial."""
        return self._repo.get_all()

    def obtener_por_vehiculo(self, id_vehiculo: int) -> Optional[Dict]:
        """Obtiene el historial para un vehículo específico."""
        return self._repo.get_by_vehiculo(id_vehiculo)

    def crear(self, id_vehiculo: int, kilometraje_ingreso: int,
                fecha_servicio: str, estado_final: str,
                diagnosticos_asociados: list = None) -> Dict:
        """
        Crea un nuevo registro en el historial.
        Resuelve la fecha y la convierte a un objeto datetime nativo
        para guardarla correctamente como ISODate en MongoDB.
        """
        # Conversión de fecha robusta
        if isinstance(fecha_servicio, str):
            try:
                fecha_dt = datetime.strptime(fecha_servicio.strip()[:10], "%Y-%m-%d")
            except Exception:
                try:
                    fecha_dt = datetime.strptime(fecha_servicio.strip(), "%d/%m/%Y")
                except Exception:
                    fecha_dt = datetime.utcnow()
        elif isinstance(fecha_servicio, datetime):
            fecha_dt = fecha_servicio
        else:
            fecha_dt = datetime.utcnow()

        return self._repo.create(
            id_vehiculo=int(id_vehiculo),
            kilometraje_ingreso=int(kilometraje_ingreso),
            fecha_servicio=fecha_dt,
            estado_final=estado_final,
            diagnosticos_asociados=diagnosticos_asociados or []
        )
