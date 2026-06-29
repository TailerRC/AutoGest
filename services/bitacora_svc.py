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

    def obtener_por_codigo(self, codigo_diagnostico: str) -> Optional[Dict]:
        return self._repo.get_by_codigo(codigo_diagnostico)

    def listar_por_vehiculo(self, id_vehiculo: int) -> List[Dict]:
        return self._repo.get_all_by_vehiculo(id_vehiculo)

    def crear(self, id_vehiculo: int, id_empleado: int, codigo_especificacion: str,
              sintomas_raw: str, codigos_raw: str, observaciones: str) -> Dict:
        """
        Reglas de negocio:
          - id_vehiculo se guarda como referencia (FK lógica hacia Oracle), sin
            re-validar su existencia: el formulario ya solo permite elegir
            vehículos reales desde el selector poblado por Oracle.
          - Síntomas y códigos OBD son strings separados por comas → se convierten en listas.
        """
        sintomas    = [s.strip() for s in sintomas_raw.split(",")  if s.strip()]
        codigos_obd = [c.strip() for c in codigos_raw.split(",")   if c.strip()]
        return self._repo.create(
            id_vehiculo, id_empleado, codigo_especificacion, sintomas, codigos_obd, observaciones
        )

    def agregar_fotos(self, codigo_diagnostico: str, urls: List[str]) -> bool:
        """
        Regla de negocio: una bitácora siempre recibe exactamente 3 fotos
        (frontal, lateral, angular) — la validación de cantidad/presencia
        de archivos vive en el controller (igual que en VehiculoService).
        """
        if len(urls) != 3:
            raise ValueError("Se requieren exactamente 3 fotos: frontal, lateral y angular.")
        return self._repo.agregar_fotos(codigo_diagnostico, urls)
