"""
repositories/oracle/usuarios_repo.py
=====================================
Repositorio para la tabla USUARIOS (Oracle).
"""
from typing import List, Optional, Dict
from database import OracleDB


class UsuarioRepository:
    """
    Repositorio de usuarios del sistema.

    TODO (Oracle real): reemplazar por queries con cx_Oracle
    """

    def __init__(self, db: OracleDB):
        self._db = db

    def get_all(self) -> List[Dict]:
        """
        Usuarios enriquecidos con nombre_empleado.
        TODO: SELECT u.*, e.nombre FROM USUARIOS u
              JOIN EMPLEADOS e ON u.id_empleado=e.id_empleado
        """
        return self._db.get_all_usuarios()

    def get_by_username(self, username: str) -> Optional[Dict]:
        """
        TODO: SELECT * FROM USUARIOS WHERE username=:1
        """
        return self._db.get_usuario_by_username(username)

    def get_by_id(self, id_usuario: int) -> Optional[Dict]:
        """
        TODO: SELECT * FROM USUARIOS WHERE id_usuario=:1
        """
        return self._db.get_usuario(id_usuario)

    def create(self, id_empleado: int, username: str,
               password: str, rol: str) -> Dict:
        """
        TODO: INSERT INTO USUARIOS VALUES(SEQ_USR.NEXTVAL,:1,:2,:3,:4,'activo')
        """
        return self._db.create_usuario(id_empleado, username, password, rol)

    def update(self, id_usuario: int, username: str, rol: str,
               estado: str, password: Optional[str] = None) -> bool:
        """
        TODO: UPDATE USUARIOS SET username=:1,rol=:2,estado=:3[,password=:4] WHERE id_usuario=:5
        """
        return self._db.update_usuario(id_usuario, username, rol, estado, password)
