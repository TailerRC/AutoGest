"""
services/empleados_svc.py
==========================
Lógica de negocio para la gestión de Empleados.
"""
from typing import List, Optional, Dict
from repositories.oracle.empleados_repo import EmpleadoRepository


class EmpleadoService:
    """
    Servicio de Empleados — reglas de negocio puras.
    """

    def __init__(self, repo: EmpleadoRepository):
        self._repo = repo

    def listar(self) -> List[Dict]:
        return self._repo.get_all()

    def listar_mecanicos(self) -> List[Dict]:
        """Retorna solo los empleados con perfil de mecánico/técnico."""
        return self._repo.get_mecanicos()

    def obtener(self, id_empleado: int) -> Optional[Dict]:
        return self._repo.get_by_id(id_empleado)

    def crear(self, nombre: str, cargo: str, especialidad: str) -> Dict:
        if not nombre or not nombre.strip():
            raise ValueError("El nombre es obligatorio.")
        return self._repo.create(nombre.strip(), cargo.strip(), especialidad.strip())

    def actualizar(self, id_empleado: int, nombre: str,
                   cargo: str, especialidad: str) -> bool:
        if not self._repo.get_by_id(id_empleado):
            return False
        return self._repo.update(id_empleado, nombre.strip(),
                                  cargo.strip(), especialidad.strip())
