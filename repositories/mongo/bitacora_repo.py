"""
repositories/mongo/bitacora_repo.py
=====================================
Repositorio para la colección bitacora_diagnostico (MongoDB).
"""
from typing import List, Optional, Dict
from database import MongoDB


class BitacoraRepository:
    """
    Repositorio de bitácoras de diagnóstico.

    TODO (MongoDB real): reemplazar por operaciones pymongo/Motor:
        self._col = db["bitacora_diagnostico"]
    """

    def __init__(self, db: MongoDB):
        self._db = db

    def get_all(self) -> List[Dict]:
        """
        TODO: return list(self._col.find().sort("fecha", -1))
        """
        return self._db.get_all_bitacoras()

    def get_by_vehiculo(self, id_vehiculo: int) -> Optional[Dict]:
        """
        TODO: return self._col.find_one({"idVehiculo": id_vehiculo})
        """
        return self._db.get_bitacora_by_vehiculo(id_vehiculo)

    def create(self, id_vehiculo: int, id_empleado: int, codigo_especificacion: str,
               sintomas: List[str], codigos_obd: List[str], observaciones: str) -> Dict:
        """
        TODO: return self._col.insert_one({...}).inserted_id
        """
        return self._db.create_bitacora(
            id_vehiculo, id_empleado, codigo_especificacion, sintomas, codigos_obd, observaciones
        )
