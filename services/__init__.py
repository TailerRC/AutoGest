"""
services/
=========
Paquete de servicios — lógica de negocio pura de AutoGest.
Cada servicio depende de uno o más repositorios (no de database.py directamente).
"""
from .clientes_svc  import ClienteService
from .vehiculos_svc import VehiculoService
from .empleados_svc import EmpleadoService
from .ordenes_svc   import OrdenService
from .repuestos_svc import RepuestoService
from .facturas_svc  import FacturaService
from .usuarios_svc  import UsuarioService
from .catalogo_svc  import CatalogoService
from .bitacora_svc  import BitacoraService
from .reportes_svc  import ReporteService

__all__ = [
    "ClienteService", "VehiculoService", "EmpleadoService",
    "OrdenService", "RepuestoService", "FacturaService",
    "UsuarioService", "CatalogoService", "BitacoraService",
    "ReporteService",
]
