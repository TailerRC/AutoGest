"""
auth.py
=======
Sistema de autenticación y control de acceso por roles para AutoGest.
Gestiona sesiones en memoria y validación de permisos.
"""

from database import get_oracle_connection, get_mongo_connection
from typing import Optional, Dict
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────
# Permisos por rol
# ─────────────────────────────────────────────────────────────────────

PERMISOS = {
    "admin": {
        "modulos": ["clientes", "vehiculos", "empleados", "ordenes", "repuestos",
                    "facturas", "usuarios", "catalogo", "bitacora", "reportes", "dashboard",
                    "historial", "cotizaciones", "proveedores"],
        "acciones": ["ver", "crear", "editar", "eliminar"]
    },
    "mecanico": {
        "modulos": ["ordenes", "repuestos", "bitacora", "historial", "catalogo", "dashboard", "proveedores"],
        "acciones": ["ver", "crear"]
    },
    "facturacion": {
        "modulos": ["facturas", "ordenes", "clientes", "cotizaciones", "dashboard"],
        "acciones": ["ver", "crear", "editar"]
    },
    "readonly": {
        "modulos": ["reportes", "ordenes", "facturas", "dashboard"],
        "acciones": ["ver"]
    }
}

# Menú lateral por rol
MENU_POR_ROL = {
    "admin": [
        {"href": "/dashboard",   "icon": "fa-solid fa-house",            "label": "Dashboard"},
        {"href": "/clientes",    "icon": "fa-solid fa-users",            "label": "Clientes"},
        {"href": "/vehiculos",   "icon": "fa-solid fa-car",              "label": "Vehículos"},
        {"href": "/empleados",   "icon": "fa-solid fa-helmet-safety",    "label": "Empleados"},
        {"href": "/ordenes",     "icon": "fa-solid fa-clipboard-list",   "label": "Órdenes de Trabajo"},
        {"href": "/repuestos",   "icon": "fa-solid fa-screwdriver-wrench","label": "Inventario Repuestos"},
        {"href": "/facturas",    "icon": "fa-solid fa-file-invoice-dollar","label": "Facturas"},
        {"href": "/usuarios",    "icon": "fa-solid fa-user-shield",      "label": "Usuarios"},
        {"href": "/catalogo",    "icon": "fa-solid fa-book-open",        "label": "Catálogo Técnico"},
        {"href": "/bitacora",    "icon": "fa-solid fa-book",             "label": "Bitácora Diagnóstico"},
        {"href": "/reportes",    "icon": "fa-solid fa-chart-bar",        "label": "Reportes"},
        {"href": "/historial",   "icon": "fa-solid fa-clock-rotate-left","label": "Historial Mantenimiento"},
        {"href": "/cotizaciones","icon": "fa-solid fa-file-contract",    "label": "Cotizaciones"},
        {"href": "/proveedores", "icon": "fa-solid fa-truck-fast",       "label": "Proveedores"},
    ],
    "mecanico": [
        {"href": "/dashboard",   "icon": "fa-solid fa-house",            "label": "Dashboard"},
        {"href": "/ordenes",     "icon": "fa-solid fa-clipboard-list",   "label": "Órdenes de Trabajo"},
        {"href": "/repuestos",   "icon": "fa-solid fa-screwdriver-wrench","label": "Inventario Repuestos"},
        {"href": "/catalogo",    "icon": "fa-solid fa-book-open",        "label": "Catálogo Técnico"},
        {"href": "/bitacora",    "icon": "fa-solid fa-book",             "label": "Bitácora Diagnóstico"},
        {"href": "/historial",   "icon": "fa-solid fa-clock-rotate-left","label": "Historial Mantenimiento"},
        {"href": "/proveedores", "icon": "fa-solid fa-truck-fast",       "label": "Proveedores"},
    ],
    "facturacion": [
        {"href": "/dashboard",   "icon": "fa-solid fa-house",            "label": "Dashboard"},
        {"href": "/clientes",    "icon": "fa-solid fa-users",            "label": "Clientes"},
        {"href": "/ordenes",     "icon": "fa-solid fa-clipboard-list",   "label": "Órdenes de Trabajo"},
        {"href": "/facturas",    "icon": "fa-solid fa-file-invoice-dollar","label": "Facturas"},
        {"href": "/cotizaciones","icon": "fa-solid fa-file-contract",    "label": "Cotizaciones"},
    ],
    "readonly": [
        {"href": "/dashboard",   "icon": "fa-solid fa-house",            "label": "Dashboard"},
        {"href": "/ordenes",     "icon": "fa-solid fa-clipboard-list",   "label": "Órdenes de Trabajo"},
        {"href": "/facturas",    "icon": "fa-solid fa-file-invoice-dollar","label": "Facturas"},
        {"href": "/reportes",    "icon": "fa-solid fa-chart-bar",        "label": "Reportes"},
    ],
}

# ─────────────────────────────────────────────────────────────────────
# Almacén de sesiones en memoria (simulando una cookie/JWT store)
# ─────────────────────────────────────────────────────────────────────
_sessions: Dict[str, Dict] = {}

def login(username: str, password: str) -> Optional[Dict]:
    """
    Autentica al usuario contra la tabla USUARIOS (mock Oracle).
    Retorna el usuario si es válido y activo, o None si falla.
    """
    db = get_oracle_connection()
    mongo = get_mongo_connection()
    
    usuario = db.get_usuario_by_username(username)
    
    if not usuario:
        mongo.registrar_log(0, "LOGIN_FALLIDO", "auth", f"usuario_no_existe:{username}")
        return None
    
    if usuario["password"] != password:
        mongo.registrar_log(usuario["id_empleado"], "LOGIN_FALLIDO", "auth", "contraseña_incorrecta")
        return None
    
    if usuario["estado"] != "activo":
        mongo.registrar_log(usuario["id_empleado"], "LOGIN_FALLIDO", "auth", "usuario_inactivo")
        return None
    
    # Login exitoso
    mongo.registrar_log(usuario["id_empleado"], "LOGIN", "auth", "exitoso")
    return usuario


def puede_acceder(usuario: Dict, modulo: str, accion: str = "ver") -> bool:
    """
    Verifica si el usuario tiene permiso para acceder a un módulo con una acción específica.
    """
    if not usuario:
        return False
    rol = usuario.get("rol", "readonly")
    permisos = PERMISOS.get(rol, {})
    modulos_ok = modulo in permisos.get("modulos", [])
    accion_ok = accion in permisos.get("acciones", [])
    return modulos_ok and accion_ok


def get_menu(usuario: Dict) -> list:
    """Retorna los ítems de menú según el rol del usuario."""
    if not usuario:
        return []
    return MENU_POR_ROL.get(usuario.get("rol", "readonly"), [])


def registrar_accion(usuario: Dict, accion: str, modulo: str, resultado: str = "exitoso"):
    """Registra una acción en el log de MongoDB."""
    mongo = get_mongo_connection()
    id_emp = usuario.get("id_empleado", 0) if usuario else 0
    mongo.registrar_log(id_emp, accion, modulo, resultado)
