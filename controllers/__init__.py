"""
controllers/__init__.py
=======================
Contenedor de dependencias para AutoGest.
Instancia los repositorios y servicios una sola vez (singleton pattern),
de modo que todos los controllers los compartan.

Uso en controllers:
    from controllers import deps
    deps.clientes.listar()
"""
from database import get_oracle_connection, get_mongo_connection

# ── Repositorios Oracle ────────────────────────────────────────────────
from repositories.oracle.clientes_repo  import ClienteRepository
from repositories.oracle.vehiculos_repo import VehiculoRepository
from repositories.oracle.empleados_repo import EmpleadoRepository
from repositories.oracle.ordenes_repo   import OrdenRepository
from repositories.oracle.repuestos_repo import RepuestoRepository
from repositories.oracle.facturas_repo  import FacturaRepository
from repositories.oracle.usuarios_repo  import UsuarioRepository

# ── Repositorios Mongo ─────────────────────────────────────────────────
from repositories.mongo.catalogo_repo   import CatalogoRepository
from repositories.mongo.bitacora_repo   import BitacoraRepository
from repositories.mongo.logs_repo       import LogsRepository
from repositories.mongo.historial_repo  import HistorialRepository
from repositories.mongo.cotizaciones_repo import CotizacionesRepository
from repositories.mongo.proveedores_repo import ProveedoresRepository

# ── Servicios ──────────────────────────────────────────────────────────
from services.clientes_svc  import ClienteService
from services.vehiculos_svc import VehiculoService
from services.empleados_svc import EmpleadoService
from services.ordenes_svc   import OrdenService
from services.repuestos_svc import RepuestoService
from services.facturas_svc  import FacturaService
from services.usuarios_svc  import UsuarioService
from services.catalogo_svc  import CatalogoService
from services.bitacora_svc  import BitacoraService
from services.reportes_svc  import ReporteService
from services.historial_svc import HistorialService
from services.cotizaciones_svc import CotizacionesService
from services.proveedores_svc import ProveedoresService
from services.alertas_svc import AlertaService

class _DependencyContainer:
    """Inicializa y expone todos los servicios listos para usar."""

    def __init__(self):
        # Conexiones
        _oracle = get_oracle_connection()
        _mongo  = get_mongo_connection()

        # Repositorios Oracle
        _cli_repo = ClienteRepository(_oracle)
        _veh_repo = VehiculoRepository(_oracle)
        _emp_repo = EmpleadoRepository(_oracle)
        _ord_repo = OrdenRepository(_oracle)
        _rep_repo = RepuestoRepository(_oracle)
        _fac_repo = FacturaRepository(_oracle)
        _usr_repo = UsuarioRepository(_oracle)

        # Repositorios Mongo
        _cat_repo = CatalogoRepository(_mongo)
        _bit_repo = BitacoraRepository(_mongo)
        _log_repo = LogsRepository(_mongo)
        _his_repo = HistorialRepository(_mongo)
        _cot_repo = CotizacionesRepository(_mongo)
        _pro_repo = ProveedoresRepository(_mongo)

        # Servicios (dependencias ya resueltas)
        self.clientes  = ClienteService(_cli_repo)
        self.vehiculos = VehiculoService(_veh_repo, _cli_repo)
        self.empleados = EmpleadoService(_emp_repo)
        self.ordenes   = OrdenService(_ord_repo, _rep_repo)
        self.repuestos = RepuestoService(_rep_repo)
        self.facturas  = FacturaService(_fac_repo, _ord_repo)
        self.usuarios  = UsuarioService(_usr_repo)
        self.catalogo  = CatalogoService(_cat_repo)
        self.bitacora  = BitacoraService(_bit_repo, _ord_repo)
        self.reportes  = ReporteService(
            _ord_repo, _fac_repo, _rep_repo,
            _bit_repo, _cat_repo, _log_repo
        )
        self.logs      = _log_repo   # acceso directo al repo de logs
        self.historial = HistorialService(_his_repo, _veh_repo)
        self.cotizaciones = CotizacionesService(_cot_repo)
        self.proveedores  = ProveedoresService(_pro_repo)
        self.alertas    = AlertaService(_log_repo, _ord_repo, _fac_repo, _rep_repo)


# Singleton — se inicializa una sola vez al importar el paquete
deps = _DependencyContainer()

__all__ = ["deps"]
