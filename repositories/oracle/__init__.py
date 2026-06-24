"""
repositories/oracle/
====================
Repositorios para las 7 entidades Oracle del sistema AutoGest.
"""
from .clientes_repo  import ClienteRepository
from .vehiculos_repo import VehiculoRepository
from .empleados_repo import EmpleadoRepository
from .ordenes_repo   import OrdenRepository
from .repuestos_repo import RepuestoRepository
from .facturas_repo  import FacturaRepository
from .usuarios_repo  import UsuarioRepository

__all__ = [
    "ClienteRepository", "VehiculoRepository", "EmpleadoRepository",
    "OrdenRepository", "RepuestoRepository", "FacturaRepository",
    "UsuarioRepository",
]
