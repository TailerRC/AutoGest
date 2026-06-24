"""
services/clientes_svc.py
=========================
Lógica de negocio para la gestión de Clientes.
Solo depende del repositorio, nunca de database.py ni HTTP.
"""
from typing import List, Optional, Dict
from repositories.oracle.clientes_repo import ClienteRepository


class ClienteService:
    """
    Servicio de Clientes — reglas de negocio puras.
    """

    def __init__(self, repo: ClienteRepository):
        self._repo = repo

    def listar(self) -> List[Dict]:
        """Retorna la lista completa de clientes."""
        return self._repo.get_all()

    def obtener(self, id_cliente: int) -> Optional[Dict]:
        """Retorna un cliente o None si no existe."""
        return self._repo.get_by_id(id_cliente)

    def crear(self, nombre: str, dni: str, telefono: str, email: str) -> Dict:
        """
        Crea un nuevo cliente.
        Reglas de negocio:
          - nombre y DNI son obligatorios (validado antes de llamar).
          - El DNI debe tener exactamente 8 caracteres.
        """
        if not nombre or not nombre.strip():
            raise ValueError("El nombre es obligatorio.")
        if not dni or len(dni.strip()) != 8:
            raise ValueError("El DNI debe tener 8 dígitos.")
        return self._repo.create(
            nombre.strip(), telefono.strip(), dni.strip(), email.strip()
        )

    def actualizar(self, id_cliente: int, nombre: str, dni: str,
                   telefono: str, email: str) -> bool:
        """
        Actualiza un cliente existente.
        Retorna False si el cliente no existe.
        """
        cliente = self._repo.get_by_id(id_cliente)
        if not cliente:
            return False
        return self._repo.update(
            id_cliente, nombre.strip(), telefono.strip(), dni.strip(), email.strip()
        )

    def eliminar(self, id_cliente: int) -> bool:
        """
        Elimina un cliente.
        Retorna False si el cliente no existe.
        """
        return self._repo.delete(id_cliente)
