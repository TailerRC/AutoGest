"""
services/vehiculos_svc.py
==========================
Lógica de negocio para la gestión de Vehículos.
"""
from typing import List, Optional, Dict
from repositories.oracle.vehiculos_repo import VehiculoRepository
from repositories.oracle.clientes_repo  import ClienteRepository


class VehiculoService:
    """
    Servicio de Vehículos — reglas de negocio puras.
    """

    def __init__(self, repo: VehiculoRepository, cliente_repo: ClienteRepository):
        self._repo         = repo
        self._cliente_repo = cliente_repo

    def listar(self) -> List[Dict]:
        return self._repo.get_all()

    def obtener(self, id_vehiculo: int) -> Optional[Dict]:
        return self._repo.get_by_id(id_vehiculo)

    def crear(self, id_cliente: int, placa: str, marca: str,
              modelo: str, anio: int) -> Dict:
        """
        Reglas de negocio:
          - El cliente debe existir.
          - La placa se guarda en mayúsculas.
        """
        if not self._cliente_repo.get_by_id(id_cliente):
            raise ValueError(f"El cliente #{id_cliente} no existe.")
        return self._repo.create(id_cliente, placa.upper(), marca, modelo, anio)

    def actualizar(self, id_vehiculo: int, id_cliente: int, placa: str,
                   marca: str, modelo: str, anio: int) -> bool:
        if not self._repo.get_by_id(id_vehiculo):
            return False
        return self._repo.update(id_vehiculo, id_cliente, placa.upper(),
                                  marca, modelo, anio)

    def eliminar(self, id_vehiculo: int) -> bool:
        return self._repo.delete(id_vehiculo)
