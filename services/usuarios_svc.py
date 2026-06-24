"""
services/usuarios_svc.py
=========================
Lógica de negocio para la gestión de Usuarios del sistema.
"""
from typing import List, Optional, Dict
from repositories.oracle.usuarios_repo import UsuarioRepository
from security import hash_password


class UsuarioService:
    """
    Servicio de Usuarios — reglas de negocio puras.
    """

    ROLES_VALIDOS   = {"admin", "mecanico", "facturacion", "readonly"}
    ESTADOS_VALIDOS = {"activo", "inactivo"}

    def __init__(self, repo: UsuarioRepository):
        self._repo = repo

    def listar(self) -> List[Dict]:
        return self._repo.get_all()

    def obtener(self, id_usuario: int) -> Optional[Dict]:
        return self._repo.get_by_id(id_usuario)

    def crear(self, id_empleado: int, username: str,
              password: str, rol: str) -> Dict:
        """
        Reglas de negocio:
          - El username debe ser único.
          - El rol debe ser uno de los válidos.
        """
        if rol not in self.ROLES_VALIDOS:
            raise ValueError(f"Rol inválido: {rol}")
        if self._repo.get_by_username(username):
            raise ValueError(f"El username '{username}' ya está en uso.")
        hashed_pwd = hash_password(password)
        return self._repo.create(id_empleado, username, hashed_pwd, rol)

    def actualizar(self, id_usuario: int, id_empleado: int, username: str,
                   password: str, rol: str, estado: str) -> bool:
        if rol not in self.ROLES_VALIDOS:
            raise ValueError(f"Rol inválido: {rol}")
        if estado not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido: {estado}")
        # Verificar que el nuevo username no lo use otro usuario
        existente = self._repo.get_by_username(username)
        if existente and existente["id_usuario"] != id_usuario:
            raise ValueError(f"El username '{username}' ya está en uso.")
        
        final_password = None
        if password and password.strip():
            final_password = hash_password(password)
            
        return self._repo.update(
            id_usuario, username, rol, estado, final_password
        )

    def desactivar(self, id_usuario: int) -> bool:
        """Desactiva un usuario sin eliminarlo."""
        usuario = self._repo.get_by_id(id_usuario)
        if not usuario:
            return False
        return self._repo.update(
            id_usuario, usuario["username"], usuario["rol"], "inactivo"
        )
