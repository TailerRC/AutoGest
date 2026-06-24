"""
models/schemas/
===============
Schemas Pydantic que definen los contratos de datos de AutoGest.
Sirven como documentación viva del modelo de datos y como
capa de validación de entrada en los services.
"""
from .cliente  import ClienteCreate, ClienteUpdate, ClienteOut
from .vehiculo import VehiculoCreate, VehiculoUpdate, VehiculoOut
from .empleado import EmpleadoCreate, EmpleadoUpdate, EmpleadoOut
from .orden    import OrdenCreate, OrdenUpdate, OrdenOut
from .repuesto import RepuestoCreate, RepuestoUpdate, RepuestoOut
from .factura  import FacturaCreate, FacturaOut
from .usuario  import UsuarioCreate, UsuarioUpdate, UsuarioOut

__all__ = [
    "ClienteCreate", "ClienteUpdate", "ClienteOut",
    "VehiculoCreate", "VehiculoUpdate", "VehiculoOut",
    "EmpleadoCreate", "EmpleadoUpdate", "EmpleadoOut",
    "OrdenCreate", "OrdenUpdate", "OrdenOut",
    "RepuestoCreate", "RepuestoUpdate", "RepuestoOut",
    "FacturaCreate", "FacturaOut",
    "UsuarioCreate", "UsuarioUpdate", "UsuarioOut",
]
