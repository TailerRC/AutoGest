"""
routes/usuarios.py — View puro de Usuarios
==========================================
Solo renderiza HTML. Lógica en controllers/usuarios_ctrl.py.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout, badge_estado, badge_rol

ROLES = ["admin", "mecanico", "facturacion", "readonly"]


def render_usuarios_list(req, usuario, usuarios):
    """Renderiza la lista de usuarios del sistema."""
    msg = req.query_params.get("msg", "")
    alerts_map = {
        "creado":      Div("✅ Usuario creado.", cls="alert alert-success"),
        "editado":     Div("✅ Usuario actualizado.", cls="alert alert-success"),
        "desactivado": Div("⚠️ Usuario desactivado.", cls="alert alert-warning"),
    }
    alert = alerts_map.get(msg, "")

    filas = []
    for u in usuarios:
        es_yo = u["username"] == usuario.get("username")
        acciones = []
        if not es_yo:
            acciones.append(A("✏️ Editar", href=f"/usuarios/{u['id_usuario']}/editar", cls="btn btn-sm btn-blue"))
            if u["estado"] == "activo":
                acciones.append(
                    Form(
                        Input(type="hidden", name="id_usuario", value=str(u["id_usuario"])),
                        Button("🚫 Desactivar", type="submit", cls="btn btn-sm btn-danger",
                               onclick="return confirm('¿Desactivar este usuario?')"),
                        method="post", action="/usuarios/desactivar"
                    )
                )
        else:
            acciones.append(Span("(sesión actual)", cls="text-muted text-sm"))

        filas.append(Tr(
            Td(f"#{u['id_usuario']}", cls="font-mono text-muted text-sm"),
            Td(u["username"], style="font-weight:600;"),
            Td(u["nombre_empleado"]),
            Td(badge_rol(u["rol"])),
            Td(badge_estado(u["estado"])),
            Td(Div(*acciones, cls="flex gap-1") if acciones else "—"),
        ))

    tabla = Div(
        Table(
            Thead(Tr(Th("#"), Th("Username"), Th("Empleado"), Th("Rol"), Th("Estado"), Th("Acciones"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("Sin usuarios.", colspan="6", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    contenido = Div(
        alert,
        Div(
            Div(H2("🔐 Gestión de Usuarios"), cls="card-header"),
            Div(
                Div(Span(f"{len(usuarios)} usuarios", cls="text-muted text-sm"),
                    A("＋ Nuevo Usuario", href="/usuarios/nuevo", cls="btn btn-primary"),
                    cls="flex gap-2", style="justify-content:space-between;align-items:center;margin-bottom:1rem;"),
                tabla, cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Usuarios", "🔐 Gestión de Usuarios", "Solo accesible para Admin — Oracle", contenido)


def render_usuarios_nuevo(req, empleados):
    """Renderiza el formulario de nuevo usuario."""
    error = req.query_params.get("error", "")
    alert = Div(f"❌ {error}", cls="alert alert-error") if error else ""

    opts_e = [Option(f"{e['nombre']} ({e['cargo']})", value=str(e["id_empleado"])) for e in empleados]

    form = Form(
        alert,
        Div(
            Div(Label("Empleado vinculado"), Select(Option("-- Seleccionar --", value=""), *opts_e, name="id_empleado", required=True), cls="form-group"),
            Div(Label("Username"), Input(name="username", placeholder="juan.perez", required=True, autocomplete="off"), cls="form-group"),
            Div(Label("Contraseña"), Input(name="password", type="password", placeholder="••••••••", required=True, autocomplete="new-password"), cls="form-group"),
            Div(Label("Rol"),
                Select(*[Option(r.capitalize(), value=r) for r in ROLES], name="rol", required=True),
                cls="form-group"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/usuarios", cls="btn btn-secondary"),
            Button("💾 Crear Usuario", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/usuarios/crear"
    )

    contenido = Div(
        Div(
            Div(H2("👤 Nuevo Usuario"), A("← Volver", href="/usuarios", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nuevo Usuario", "👤 Nuevo Usuario", "", contenido)


def render_usuarios_editar(req, u, empleados):
    """Renderiza el formulario de edición de un usuario."""
    id_usuario = u["id_usuario"]
    error = req.query_params.get("error", "")
    alert = Div(f"❌ {error}", cls="alert alert-error") if error else ""

    opts_e = [Option(f"{e['nombre']}", value=str(e["id_empleado"]), selected=(e["id_empleado"] == u["id_empleado"])) for e in empleados]

    form = Form(
        alert,
        Div(
            Div(Label("Empleado"),  Select(*opts_e, name="id_empleado", required=True), cls="form-group"),
            Div(Label("Username"), Input(name="username", value=u["username"], required=True), cls="form-group"),
            Div(Label("Nueva contraseña (dejar vacío = no cambiar)"),
                Input(name="password", type="password", placeholder="••••••••", autocomplete="new-password"),
                cls="form-group"),
            Div(Label("Rol"),
                Select(*[Option(r.capitalize(), value=r, selected=(r == u["rol"])) for r in ROLES],
                       name="rol", required=True),
                cls="form-group"),
            Div(Label("Estado"),
                Select(
                    Option("Activo",   value="activo",   selected=(u["estado"] == "activo")),
                    Option("Inactivo", value="inactivo", selected=(u["estado"] == "inactivo")),
                    name="estado", required=True
                ),
                cls="form-group"),
            cls="form-grid"
        ),
        Input(type="hidden", name="id_usuario", value=str(id_usuario)),
        Div(
            A("Cancelar", href="/usuarios", cls="btn btn-secondary"),
            Button("💾 Actualizar", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/usuarios/actualizar"
    )

    contenido = Div(
        Div(
            Div(H2(f"✏️ Editar Usuario: {u['username']}"), A("← Volver", href="/usuarios", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Editar Usuario", f"✏️ {u['username']}", "", contenido)
