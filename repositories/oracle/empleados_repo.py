"""
repositories/oracle/empleados_repo.py
======================================
Repositorio para la tabla EMPLEADOS (Oracle).
"""
from typing import List, Optional, Dict
from database import OracleDB


class EmpleadoRepository:
    """
    Repositorio de empleados.

    TODO (Oracle real): reemplazar por queries con cx_Oracle
    """

    def __init__(self, db: OracleDB):
        self._db = db

    def get_all(self) -> List[Dict]:
        """
        TODO: SELECT * FROM EMPLEADOS ORDER BY nombre
        """
        return self._db.get_all_empleados()

    def get_by_id(self, id_empleado: int) -> Optional[Dict]:
        """
        TODO: SELECT * FROM EMPLEADOS WHERE id_empleado=:1
        """
        return self._db.get_empleado(id_empleado)

    def get_mecanicos(self) -> List[Dict]:
        """
        Filtra empleados que tienen rol de mecánico/técnico.
        TODO: SELECT * FROM EMPLEADOS WHERE cargo IN ('Mecánico','Mecánico Senior','Jefe de Taller')
        """
        empleados = self._db.get_all_empleados()
        cargos_taller = {"Jefe de Taller", "Mecánico Senior", "Mecánico", "Electricista Automotriz"}
        resultado = [
            e for e in empleados
            if e.get("cargo") in cargos_taller
            or "mecánic" in (e.get("especialidad") or "").lower()
        ]
        return resultado or empleados  # fallback si no hay mecánicos

    def create(self, nombre: str, cargo: str, especialidad: str) -> Dict:
        """
        TODO: INSERT INTO EMPLEADOS VALUES(SEQ_EMP.NEXTVAL,:1,:2,:3)
        """
        return self._db.create_empleado(nombre, cargo, especialidad)

    def update(self, id_empleado: int, nombre: str, cargo: str,
               especialidad: str) -> bool:
        """
        TODO: UPDATE EMPLEADOS SET nombre=:1,cargo=:2,especialidad=:3 WHERE id_empleado=:4
        """
        return self._db.update_empleado(id_empleado, nombre, cargo, especialidad)
