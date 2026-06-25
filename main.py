"""
main.py — AutoGest: Sistema de Gestión de Taller Mecánico y Concesionaria
Universidad Ricardo Palma — Base de Datos II

Arquitectura híbrida:
  - Oracle simulado (8 tablas relacionales) → mock_data/oracle_data.py
  - MongoDB simulado (7 colecciones) → mock_data/mongo_data.py

Para ejecutar:
  python main.py   (o:  uvicorn main:app --reload)

Usuarios de prueba:
  admin       / admin123   → acceso total
  mecanico1   / mec2026    → mecánico
  facturacion / fact2026   → facturación
  readonly    / view2026   → solo lectura
"""

from fasthtml.common import *
from auth import login, puede_acceder, registrar_accion
from database import get_oracle_connection, get_mongo_connection
import os
from dotenv import load_dotenv
from starlette.datastructures import UploadFile

FOTOS_PATH = os.getenv("FOTOS_VEHICULOS_PATH", "fotos_vehiculos")

# ── Importar helpers ──────────────────────────────────────────────────
from routes.helpers import layout, login_layout, no_perm, badge_estado

# ── Importar módulos de controllers ───────────────────────────────────
from controllers.clientes_ctrl import (
    ctrl_clientes_list, ctrl_clientes_nuevo, ctrl_clientes_crear,
    ctrl_clientes_editar, ctrl_clientes_actualizar, ctrl_clientes_eliminar,
)
from controllers.vehiculos_ctrl import (
    ctrl_vehiculos_list, ctrl_vehiculos_nuevo, ctrl_vehiculos_crear,
    ctrl_vehiculos_editar, ctrl_vehiculos_actualizar, ctrl_vehiculos_eliminar,
)
from controllers.empleados_ctrl import (
    ctrl_empleados_list, ctrl_empleados_nuevo, ctrl_empleados_crear,
    ctrl_empleados_editar, ctrl_empleados_actualizar, ctrl_empleados_eliminar,
)
from controllers.ordenes_ctrl import (
    ctrl_ordenes_list, ctrl_ordenes_detalle, ctrl_ordenes_nueva, ctrl_ordenes_crear,
    ctrl_ordenes_editar, ctrl_ordenes_actualizar, ctrl_ordenes_cambiar_estado,
    ctrl_ordenes_agregar_repuesto,
)
from controllers.repuestos_ctrl import (
    ctrl_repuestos_list, ctrl_repuestos_nuevo, ctrl_repuestos_crear,
    ctrl_repuestos_editar, ctrl_repuestos_actualizar, ctrl_repuestos_eliminar,
)
from controllers.facturas_ctrl import (
    ctrl_facturas_list, ctrl_facturas_detalle, ctrl_facturas_nueva,
    ctrl_facturas_crear, ctrl_facturas_cambiar_estado,
)
from controllers.usuarios_ctrl import (
    ctrl_usuarios_list, ctrl_usuarios_nuevo, ctrl_usuarios_crear,
    ctrl_usuarios_editar, ctrl_usuarios_actualizar, ctrl_usuarios_desactivar,
)
from controllers.catalogo_ctrl import ctrl_catalogo_list
from controllers.bitacora_ctrl import (
    ctrl_bitacora_list, ctrl_bitacora_nueva, ctrl_bitacora_crear, ctrl_bitacora_detalle
)
from controllers.reportes_ctrl import ctrl_reportes_list, ctrl_reportes_detalle

from controllers.historial_ctrl import ctrl_historial_list, ctrl_historial_nuevo, ctrl_historial_crear
from controllers.cotizaciones_ctrl import (
    ctrl_cotizaciones_list, ctrl_cotizaciones_nueva, ctrl_cotizaciones_crear, ctrl_cotizaciones_detalle
)
from controllers.proveedores_ctrl import (
    ctrl_proveedores_list, ctrl_proveedores_nuevo, ctrl_proveedores_crear,
    ctrl_proveedores_editar, ctrl_proveedores_actualizar
)

load_dotenv()

# ═══════════════════════════════════════════════════════════════════════
# Inicialización de la aplicación FastHTML
# ═══════════════════════════════════════════════════════════════════════
app, rt = fast_app(
    secret_key=os.getenv("SECRET_KEY", "dev_secret_key"),
    static_path="static",
    hdrs=(
        Link(rel="stylesheet", href="/fontawesome/css/all.min.css"),
        Link(rel="stylesheet", href="/styles/styles.css"),
    ),
    live=False,
)


# ═══════════════════════════════════════════════════════════════════════
# Middleware — verificar sesión en cada petición protegida
# ═══════════════════════════════════════════════════════════════════════
def require_login(req) -> bool:
    """Retorna True si el usuario está logueado, False si no."""
    return bool(req.session.get("usuario"))


# ═══════════════════════════════════════════════════════════════════════
# RUTAS DE AUTENTICACIÓN
# ═══════════════════════════════════════════════════════════════════════

@rt("/")
def get(req):
    """Redirige al login o al dashboard según sesión."""
    if require_login(req):
        return RedirectResponse("/dashboard", status_code=303)
    return RedirectResponse("/login", status_code=303)


@rt("/login")
def get(req):
    """Pantalla de login."""
    if require_login(req):
        return RedirectResponse("/dashboard", status_code=303)

    error = req.query_params.get("error", "")
    alert = Div(f"❌ {error}", cls="alert alert-error") if error else ""

    form = Form(
        Div(
            Div(
                Img(src="/image/Logo.png", alt="AutoGest"),
                cls="logo-img-wrap"
            ),
            H1("AutoGest"),
            P("Sistema de Gestión de Taller Mecánico (Autogest)"),
            cls="login-logo"
        ),
        alert,
        Div(
            Div(
                Label("Usuario", style="font-size:.78rem;font-weight:600;color:var(--text-secondary);text-transform:uppercase;letter-spacing:.05em;"),
                Input(name="username", placeholder="Ingresa tu usuario", required=True,
                      autocomplete="username", id="username"),
                style="display:flex;flex-direction:column;gap:.4rem;margin-bottom:1rem;"
            ),
            Div(
                Label("Contraseña", style="font-size:.78rem;font-weight:600;color:var(--text-secondary);text-transform:uppercase;letter-spacing:.05em;"),
                Input(name="password", type="password", placeholder="••••••••",
                      required=True, autocomplete="current-password", id="password"),
                style="display:flex;flex-direction:column;gap:.4rem;margin-bottom:1.25rem;"
            ),
        ),
        Button(I(cls="fa-solid fa-right-to-bracket"), " Iniciar Sesión", type="submit", cls="btn btn-primary btn-full btn-lg"),
        Div(
            P("Usuarios de demo:"),
            Div(
                Span("ana.gomez / admin123", cls="badge badge-purple"),
                Span("pedro.ramirez / mec2026", cls="badge badge-blue"),
                Span("luis.torres / fact2026", cls="badge badge-orange"),
                Span("diego.vargas / view2026", cls="badge badge-gray"),
                style="display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.5rem;"
            ),
            style="margin-top:1.25rem;padding-top:1rem;border-top:1px solid var(--border);font-size:.75rem;color:var(--text-muted);"
        ),
        method="post", action="/login",
        style="display:flex;flex-direction:column;"
    )

    return login_layout("Iniciar Sesión", Div(form, cls="login-card"))


@rt("/login")
def post(req, username: str, password: str):
    """Procesa el login."""
    usuario = login(username, password)
    if not usuario:
        return RedirectResponse("/login?error=Usuario+o+contraseña+incorrectos", status_code=303)
    req.session["usuario"] = usuario
    return RedirectResponse("/dashboard", status_code=303)


@rt("/logout")
def get(req):
    """Cierra sesión."""
    usuario = req.session.get("usuario")
    if usuario:
        registrar_accion(usuario, "LOGOUT", "auth")
    req.session.clear()
    return RedirectResponse("/login", status_code=303)


# ═══════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════

@rt("/dashboard")
def get(req):
    if not require_login(req):
        return RedirectResponse("/login", status_code=303)

    usuario = req.session.get("usuario")
    db = get_oracle_connection()
    mongo = get_mongo_connection()

    clientes   = db.get_all_clientes()
    vehiculos  = db.get_all_vehiculos()
    ordenes    = db.get_all_ordenes()
    repuestos  = db.get_all_repuestos()
    facturas   = db.get_all_facturas()
    alertas    = mongo.get_alertas_activas()
    bitacoras  = mongo.get_all_bitacoras()

    pendientes  = sum(1 for o in ordenes if o["estado"] == "pendiente")
    en_proceso  = sum(1 for o in ordenes if o["estado"] == "en_proceso")
    completadas = sum(1 for o in ordenes if o["estado"] == "completada")
    criticos    = sum(1 for r in repuestos if r["stock"] <= 2)
    pendiente_cobro = sum(f["total"] for f in facturas if f["estado_pago"] == "pendiente")

    stats = Div(
        Div(Div(I(cls="fa-solid fa-users"), cls="stat-icon cyan"),    Div(Div(str(len(clientes)),  cls="stat-value"), Div("Clientes",      cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div(I(cls="fa-solid fa-car"),   cls="stat-icon blue"),    Div(Div(str(len(vehiculos)), cls="stat-value"), Div("Vehículos",     cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div(I(cls="fa-solid fa-clipboard-list"), cls="stat-icon indigo"), Div(Div(str(len(ordenes)), cls="stat-value"), Div("Órdenes", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div(I(cls="fa-solid fa-gears"), cls="stat-icon blue"),    Div(Div(str(en_proceso),     cls="stat-value"), Div("En Proceso",    cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div(I(cls="fa-solid fa-clock"), cls="stat-icon yellow"),  Div(Div(str(pendientes),     cls="stat-value"), Div("Pendientes",    cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div(I(cls="fa-solid fa-triangle-exclamation"), cls="stat-icon red"), Div(Div(str(criticos), cls="stat-value"), Div("Stock Crítico", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div(I(cls="fa-solid fa-file-invoice"), cls="stat-icon teal"), Div(Div(str(len(facturas)), cls="stat-value"), Div("Facturas",   cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div(I(cls="fa-solid fa-sack-dollar"), cls="stat-icon green"), Div(Div(f"S/. {pendiente_cobro:,.0f}", cls="stat-value"), Div("Por Cobrar", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        cls="stats-grid"
    )

    # Alertas del sistema (MongoDB)
    alertas_cards = []
    for a in alertas[:4]:
        prioridad_cls = "badge-red" if "Crítico" in a.get("tipo_evento", "") or "Seguridad" in a.get("tipo_evento", "") else "badge-yellow"
        alertas_cards.append(
            Div(
                Div(
                    Span(a.get("tipo_evento", "").upper(), cls=f"badge {prioridad_cls}"),
                    Span(a.get("codigoAlerta", ""), cls="text-muted text-sm font-mono"),
                    style="display:flex;align-items:center;justify-content:space-between;"
                ),
                P(str(a.get("detalle_notificacion", {})), style="margin-top:.4rem;font-size:.85rem;color:var(--text-secondary);"),
                style="padding:.75rem;background:rgba(255,255,255,.03);border:1px solid var(--border);border-radius:var(--radius);margin-bottom:.5rem;"
            )
        )

    # Últimas órdenes
    ultimas = ordenes[-5:]
    filas_ord = [
        Tr(
            Td(f"#{o['id_orden']}", cls="font-mono text-sm"),
            Td(o.get("nombre_cliente","—")),
            Td(Span(o.get("placa",""), cls="badge badge-gray font-mono")),
            Td(badge_estado(o["estado"])),
            Td(A("Ver", href=f"/ordenes/{o['id_orden']}", cls="btn btn-sm btn-secondary")),
        )
        for o in reversed(ultimas)
    ]

    nombre_u = usuario.get("username","")
    rol_u    = usuario.get("rol","")

    contenido = Div(
        # Bienvenida
        Div(
            Div(
                Div(
                    H2(I(cls="fa-solid fa-hand-wave"), f" ¡Bienvenido, {nombre_u}!"),
                    P("Sesión activa como: ", Span(rol_u.capitalize(), cls=f"badge badge-blue"), cls="text-muted text-sm mt-1"),
                    style="flex:1;"
                ),
                Div(
                    Span(I(cls="fa-solid fa-database"), " Oracle", cls="badge badge-red"),
                    Span(I(cls="fa-solid fa-leaf"), " MongoDB", cls="badge badge-green"),
                    cls="flex gap-1", style="align-items:center;"
                ),
                cls="card-header", style="display:flex;align-items:center;justify-content:space-between;"
            ),
            cls="card mb-2"
        ),
        stats,
        # Dos columnas
        Div(
            Div(
                Div(
                    Div(H2(I(cls="fa-solid fa-clipboard-list"), " Últimas Órdenes"), Span(I(cls="fa-solid fa-database"), " Oracle", cls="db-tag oracle"), cls="card-header"),
                    Div(
                        Div(
                            Table(
                                Thead(Tr(Th("#"), Th("Cliente"), Th("Placa"), Th("Estado"), Th(""))),
                                Tbody(*filas_ord),
                            ),
                            cls="table-wrap"
                        ),
                        cls="card-body"
                    ),
                    cls="card"
                ),
                style="flex:1.5;"
            ),
            Div(
                Div(
                    Div(H2(I(cls="fa-solid fa-bell"), " Alertas del Sistema"), Span(I(cls="fa-solid fa-leaf"), " MongoDB", cls="db-tag mongo"), cls="card-header"),
                    Div(
                        *alertas_cards if alertas_cards else [P("Sin alertas activas.", cls="no-data")],
                        cls="card-body"
                    ),
                    cls="card"
                ),
                style="flex:1;"
            ),
            cls="flex gap-2", style="align-items:flex-start;"
        ),
        cls="page-body"
    )
    return layout(req, "Dashboard", "🏠 Dashboard", f"AutoGest — {len(ordenes)} órdenes activas", contenido)


# ═══════════════════════════════════════════════════════════════════════
# CLIENTES
# ═══════════════════════════════════════════════════════════════════════
@rt("/clientes")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_clientes_list(req)

@rt("/clientes/nuevo")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_clientes_nuevo(req)

@rt("/clientes/crear")
def post(req, nombre: str, dni: str, telefono: str, email: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_clientes_crear(req, nombre, dni, telefono, email)

@rt("/clientes/{id_cliente}/editar")
def get(req, id_cliente: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_clientes_editar(req, id_cliente)

@rt("/clientes/actualizar")
def post(req, id_cliente: int, nombre: str, dni: str, telefono: str, email: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_clientes_actualizar(req, id_cliente, nombre, dni, telefono, email)

@rt("/clientes/eliminar")
def post(req, id_cliente: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_clientes_eliminar(req, id_cliente)


# ═══════════════════════════════════════════════════════════════════════
# VEHÍCULOS
# ═══════════════════════════════════════════════════════════════════════
@rt("/vehiculos")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_vehiculos_list(req)

@rt("/vehiculos/nuevo")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_vehiculos_nuevo(req)

@rt("/vehiculos/crear")
def post(req, id_cliente: int, placa: str, marca: str, modelo: str, anio: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_vehiculos_crear(req, id_cliente, placa, marca, modelo, anio)

@rt("/vehiculos/{id_vehiculo}/editar")
def get(req, id_vehiculo: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_vehiculos_editar(req, id_vehiculo)

@rt("/vehiculos/actualizar")
def post(req, id_vehiculo: int, id_cliente: int, placa: str, marca: str, modelo: str, anio: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_vehiculos_actualizar(req, id_vehiculo, id_cliente, placa, marca, modelo, anio)

@rt("/vehiculos/eliminar")
def post(req, id_vehiculo: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_vehiculos_eliminar(req, id_vehiculo)

@rt("/vehiculos/{id_vehiculo}/fotos")
async def post(req, id_vehiculo: int):
    if not require_login(req):
        return RedirectResponse("/login", status_code=303)

    form     = await req.form()
    placa    = form.get("placa", "").upper().strip()
    frontal  = form.get("foto_frontal")
    lateral  = form.get("foto_lateral")
    angular  = form.get("foto_angular")

    archivos = {
        "FRONTAL": frontal,
        "LATERAL": lateral,
        "ANGULAR": angular,
    }

    # Validar que las 3 estén presentes
    for vista, archivo in archivos.items():
        if not archivo or not getattr(archivo, "filename", None):
            return RedirectResponse(
                f"/vehiculos/{id_vehiculo}/editar?error=Debes+subir+las+3+fotos+({vista}+falta)",
                status_code=303
            )

    # Crear carpeta {PLACA}_FOTOS dentro de la ruta general
    carpeta = os.path.join(FOTOS_PATH, f"{placa}_FOTOS")
    os.makedirs(carpeta, exist_ok=True)

    # Guardar cada foto
    for vista, archivo in archivos.items():
        ext     = os.path.splitext(archivo.filename)[1].lower() or ".jpg"
        nombre  = f"{placa}_{vista}{ext}"
        destino = os.path.join(carpeta, nombre)
        contenido = await archivo.read()
        with open(destino, "wb") as f:
            f.write(contenido)

    return RedirectResponse(
        f"/vehiculos/{id_vehiculo}/editar?msg=fotos_ok",
        status_code=303
    )

# ═══════════════════════════════════════════════════════════════════════
# EMPLEADOS
# ═══════════════════════════════════════════════════════════════════════
@rt("/empleados")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_empleados_list(req)

@rt("/empleados/nuevo")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_empleados_nuevo(req)

@rt("/empleados/crear")
def post(req, nombre: str, cargo: str, especialidad: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_empleados_crear(req, nombre, cargo, especialidad)

@rt("/empleados/{id_empleado}/editar")
def get(req, id_empleado: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_empleados_editar(req, id_empleado)

@rt("/empleados/actualizar")
def post(req, id_empleado: int, nombre: str, cargo: str, especialidad: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_empleados_actualizar(req, id_empleado, nombre, cargo, especialidad)

@rt("/empleados/eliminar")
def post(req, id_empleado: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_empleados_eliminar(req, id_empleado)

# ═══════════════════════════════════════════════════════════════════════
# ÓRDENES DE TRABAJO
# ═══════════════════════════════════════════════════════════════════════
@rt("/ordenes")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_ordenes_list(req)

@rt("/ordenes/nueva")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_ordenes_nueva(req)

@rt("/ordenes/crear")
def post(req, id_vehiculo: int, id_empleado: int, fecha_ingreso: str, fecha_entrega: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_ordenes_crear(req, id_vehiculo, id_empleado, fecha_ingreso, fecha_entrega)

@rt("/ordenes/{id_orden}")
def get(req, id_orden: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_ordenes_detalle(req, id_orden)

@rt("/ordenes/{id_orden}/editar")
def get(req, id_orden: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_ordenes_editar(req, id_orden)

@rt("/ordenes/actualizar")
def post(req, id_orden: int, id_vehiculo: int, id_empleado: int,
         fecha_ingreso: str, fecha_entrega: str, estado: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_ordenes_actualizar(req, id_orden, id_vehiculo, id_empleado, fecha_ingreso, fecha_entrega, estado)

@rt("/ordenes/cambiar-estado")
def post(req, id_orden: int, estado: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_ordenes_cambiar_estado(req, id_orden, estado)

@rt("/ordenes/agregar-repuesto")
def post(req, id_orden: int, id_pieza: int, cantidad: int, precio_unitario: float):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_ordenes_agregar_repuesto(req, id_orden, id_pieza, cantidad, precio_unitario)


# ═══════════════════════════════════════════════════════════════════════
# REPUESTOS / INVENTARIO
# ═══════════════════════════════════════════════════════════════════════
@rt("/repuestos")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_repuestos_list(req)

@rt("/repuestos/nuevo")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_repuestos_nuevo(req)

@rt("/repuestos/crear")
def post(req, codigo: str, nombre: str, stock: int, precio_venta: float, proveedor: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_repuestos_crear(req, codigo, nombre, stock, precio_venta, proveedor)

@rt("/repuestos/{id_pieza}/editar")
def get(req, id_pieza: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_repuestos_editar(req, id_pieza)

@rt("/repuestos/actualizar")
def post(req, id_pieza: int, codigo: str, nombre: str, stock: int, precio_venta: float, proveedor: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_repuestos_actualizar(req, id_pieza, codigo, nombre, stock, precio_venta, proveedor)

@rt("/repuestos/eliminar")
def post(req, id_pieza: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_repuestos_eliminar(req, id_pieza)


# ═══════════════════════════════════════════════════════════════════════
# FACTURAS
# ═══════════════════════════════════════════════════════════════════════
@rt("/facturas")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_facturas_list(req)

@rt("/facturas/nueva")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_facturas_nueva(req)

@rt("/facturas/crear")
def post(req, id_orden: int, total: float, metodo_pago: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_facturas_crear(req, id_orden, total, metodo_pago)

@rt("/facturas/{id_factura}")
def get(req, id_factura: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_facturas_detalle(req, id_factura)

@rt("/facturas/cambiar-estado")
def post(req, id_factura: int, estado_pago: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_facturas_cambiar_estado(req, id_factura, estado_pago)


# ═══════════════════════════════════════════════════════════════════════
# USUARIOS (solo admin)
# ═══════════════════════════════════════════════════════════════════════
@rt("/usuarios")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_usuarios_list(req)

@rt("/usuarios/nuevo")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_usuarios_nuevo(req)

@rt("/usuarios/crear")
def post(req, id_empleado: int, username: str, password: str, rol: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_usuarios_crear(req, id_empleado, username, password, rol)

@rt("/usuarios/{id_usuario}/editar")
def get(req, id_usuario: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_usuarios_editar(req, id_usuario)

@rt("/usuarios/actualizar")
def post(req, id_usuario: int, id_empleado: int, username: str,
         password: str, rol: str, estado: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_usuarios_actualizar(req, id_usuario, id_empleado, username, password, rol, estado)

@rt("/usuarios/desactivar")
def post(req, id_usuario: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_usuarios_desactivar(req, id_usuario)


# ═══════════════════════════════════════════════════════════════════════
# CATÁLOGO TÉCNICO (MongoDB)
# ═══════════════════════════════════════════════════════════════════════
@rt("/catalogo")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_catalogo_list(req)


# ═══════════════════════════════════════════════════════════════════════
# BITÁCORA DE DIAGNÓSTICO (MongoDB)
# ═══════════════════════════════════════════════════════════════════════
@rt("/bitacora")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_bitacora_list(req)

@rt("/bitacora/nueva")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_bitacora_nueva(req)

@rt("/bitacora/crear")
def post(req, id_vehiculo: int, id_empleado: int, codigo_especificacion: str,
         sintomas: str, codigos_obd: str = "", observaciones: str = ""):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_bitacora_crear(req, id_vehiculo, id_empleado, codigo_especificacion,
                               sintomas, codigos_obd, observaciones)

@rt("/bitacora/{id_orden}")
def get(req, id_orden: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_bitacora_detalle(req, id_orden)


# ═══════════════════════════════════════════════════════════════════════
# REPORTES COMBINADOS (Oracle + MongoDB)
# ═══════════════════════════════════════════════════════════════════════
@rt("/reportes")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_reportes_list(req)

@rt("/reportes/detalle")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_reportes_detalle(req)

# ═══════════════════════════════════════════════════════════════════════
# HISTORIAL, COTIZACIONES, PROVEEDORES (MongoDB)
# ═══════════════════════════════════════════════════════════════════════

# Historial
@rt("/historial")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_historial_list(req)

@rt("/historial/nuevo")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_historial_nuevo(req)

@rt("/historial/crear")
def post(req, id_vehiculo: int, kilometraje_ingreso: int, fecha_servicio: str, estado_final: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_historial_crear(req, id_vehiculo, kilometraje_ingreso, fecha_servicio, estado_final)

# Cotizaciones
@rt("/cotizaciones")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_cotizaciones_list(req)

@rt("/cotizaciones/nueva")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_cotizaciones_nueva(req)

@rt("/cotizaciones/crear")
def post(req, id_cliente: int, id_vehiculo: int, fecha_validez: str, items_json: str, total: float):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_cotizaciones_crear(req, id_cliente, id_vehiculo, fecha_validez, items_json, total)

@rt("/cotizaciones/{codigo}")
def get(req, codigo: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_cotizaciones_detalle(req, codigo)

# Proveedores
@rt("/proveedores")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_proveedores_list(req)

@rt("/proveedores/nuevo")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_proveedores_nuevo(req)

@rt("/proveedores/crear")
def post(req, codigo: str, nombre_empresa: str, lineas_raw: str, telefono: str, email: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_proveedores_crear(req, codigo, nombre_empresa, lineas_raw, telefono, email)

@rt("/proveedores/{codigo}/editar")
def get(req, codigo: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_proveedores_editar(req, codigo)

@rt("/proveedores/actualizar")
def post(req, codigo: str, nombre_empresa: str, lineas_raw: str, telefono: str, email: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_proveedores_actualizar(req, codigo, nombre_empresa, lineas_raw, telefono, email)


# ═══════════════════════════════════════════════════════════════════════
# Punto de entrada
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    import sys
    # Fix Windows console encoding
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("\n" + "="*60)
    print("  [*]  AutoGest - Sistema de Gestion de Taller Mecanico")
    print("  [U]  Universidad Ricardo Palma - Base de Datos II")
    print("="*60)
    print("\n  [>]  Abre: http://localhost:5001")
    print("\n  [i]  Usuarios de prueba:")
    print("       admin       / admin123   -> Acceso total")
    print("       mecanico1   / mec2026    -> Mecanico")
    print("       facturacion / fact2026   -> Facturacion")
    print("       readonly    / view2026   -> Solo lectura")
    print("\n" + "="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=5001, reload=False)
