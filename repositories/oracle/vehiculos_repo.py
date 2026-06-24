"""
repositories/oracle/vehiculos_repo.py
======================================
Repositorio para la tabla VEHICULOS (Oracle).
"""
from typing import List, Optional, Dict
from database import OracleDB


class VehiculoRepository:
    """
    Repositorio de vehículos.

    TODO (Oracle real): reemplazar por queries con cx_Oracle
    """

    def __init__(self, db: OracleDB):
        self._db = db

    def get_all(self) -> List[Dict]:
        """
        Retorna todos los vehículos con nombre de cliente enriquecido.
        TODO: SELECT v.*, c.nombre FROM VEHICULOS v JOIN CLIENTES c ON v.id_cliente=c.id_cliente
        """
        return self._db.get_all_vehiculos()

    def get_by_id(self, id_vehiculo: int) -> Optional[Dict]:
        """
        TODO: SELECT * FROM VEHICULOS WHERE id_vehiculo=:1
        """
        return self._db.get_vehiculo(id_vehiculo)

    def create(self, id_cliente: int, placa: str, marca: str,
               modelo: str, año: int) -> Dict:
        """
        TODO: INSERT INTO VEHICULOS VALUES(SEQ_VEH.NEXTVAL,:1,:2,:3,:4,:5)
        """
        return self._db.create_vehiculo(id_cliente, placa, marca, modelo, año)

    def update(self, id_vehiculo: int, id_cliente: int, placa: str,
               marca: str, modelo: str, año: int) -> bool:
        """
        TODO: UPDATE VEHICULOS SET id_cliente=:1,placa=:2,... WHERE id_vehiculo=:6
        """
        return self._db.update_vehiculo(id_vehiculo, id_cliente, placa, marca, modelo, año)

    def delete(self, id_vehiculo: int) -> bool:
        """
        TODO: DELETE FROM VEHICULOS WHERE id_vehiculo=:1
        """
        return self._db.delete_vehiculo(id_vehiculo)
