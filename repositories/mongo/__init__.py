"""
repositories/mongo/
===================
Repositorios para las colecciones MongoDB de AutoGest.
"""
from .catalogo_repo  import CatalogoRepository
from .bitacora_repo  import BitacoraRepository
from .logs_repo      import LogsRepository

__all__ = ["CatalogoRepository", "BitacoraRepository", "LogsRepository"]
