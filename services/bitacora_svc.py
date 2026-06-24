"""
services/bitacora_svc.py
=========================
Lógica de negocio para la Bitácora de Diagnóstico (MongoDB).
"""
from typing import List, Optional, Dict
from repositories.mongo.bitacora_repo import BitacoraRepository
from repositories.oracle.vehiculos_repo import VehiculoRepository

class BitacoraService:
    """
    Servicio de Bitácoras — reglas de negocio puras.
    """

    def __init__(self, repo: BitacoraRepository, vehiculo_repo: VehiculoRepository):
        self._repo          = repo
        self._vehiculo_repo = vehiculo_repo

    def listar(self) -> List[Dict]:
        return self._repo.get_all()

    def obtener_por_vehiculo(self, id_vehiculo: int) -> Optional[Dict]:
        return self._repo.get_by_vehiculo(id_vehiculo)

    def crear(self, id_vehiculo: int, id_empleado: int, codigo_especificacion: str,
              sintomas_raw: str, codigos_raw: str, observaciones: str) -> Dict:
        """
        Reglas de negocio:
          - El vehículo debe existir en Oracle.
          - Síntomas y códigos OBD son strings separados por comas → se convierten en listas.
        """
        if not self._vehiculo_repo.get_by_id(id_vehiculo):
            raise ValueError(f"El vehículo #{id_vehiculo} no existe en Oracle.")

        sintomas    = [s.strip() for s in sintomas_raw.split(",")  if s.strip()]
        codigos_obd = [c.strip() for c in codigos_raw.split(",")   if c.strip()]

        return self._repo.create(
            id_vehiculo, id_empleado, codigo_especificacion, sintomas, codigos_obd, observaciones
        )
