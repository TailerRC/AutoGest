"""
repositories/
=============
Paquete de repositorios — acceso a datos por entidad.
Importa los sub-paquetes oracle/ y mongo/ para acceso conveniente.
"""
from .oracle import (
    ClienteRepository,
    VehiculoRepository,
    EmpleadoRepository,
    OrdenRepository,
    RepuestoRepository,
    FacturaRepository,
    UsuarioRepository,
)
from .mongo import (
    CatalogoRepository,
    BitacoraRepository,
    LogsRepository,
)

__all__ = [
    "ClienteRepository", "VehiculoRepository", "EmpleadoRepository",
    "OrdenRepository", "RepuestoRepository", "FacturaRepository",
    "UsuarioRepository", "CatalogoRepository", "BitacoraRepository",
    "LogsRepository",
]
