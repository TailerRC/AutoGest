"""
routes/usuarios.py — Gestión de Usuarios (solo admin, Oracle simulado)
"""
from fasthtml.common import *
from database import get_oracle_connection
from auth import puede_acceder, registrar_accion
from .helpers import layout, no_perm, badge_estado, badge_rol


def usuarios_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "usuarios", "ver"):
        return no_perm(req)

    db = get_oracle_connection()
    usuarios = db.get_all_usuarios()

    msg = req.query_params.get("msg", "")
    alerts = {
        "creado":    Div("✅ Usuario creado.", cls="alert alert-success"),
        "editado":   Div("✅ Usuario actualizado.", cls="alert alert-success"),
        "desactivado": Div("⚠️ Usuario desactivado.", cls="alert alert-warning"),
    }
    alert = alerts.get(msg, "")

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


def usuarios_nuevo(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "usuarios", "crear"):
        return no_perm(req)

    db = get_oracle_connection()
    empleados = db.get_all_empleados()
    opts_e = [Option(f"{e['nombre']} ({e['cargo']})", value=str(e["id_empleado"])) for e in empleados]
    roles = ["admin", "mecanico", "facturacion", "readonly"]

    form = Form(
        Div(
            Div(Label("Empleado vinculado"), Select(Option("-- Seleccionar --", value=""), *opts_e, name="id_empleado", required=True), cls="form-group"),
            Div(Label("Username"), Input(name="username", placeholder="juan.perez", required=True, autocomplete="off"), cls="form-group"),
            Div(Label("Contraseña"), Input(name="password", type="password", placeholder="••••••••", required=True, autocomplete="new-password"), cls="form-group"),
            Div(Label("Rol"),
                Select(*[Option(r.capitalize(), value=r) for r in roles], name="rol", required=True),
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


def usuarios_crear(req, id_empleado: int, username: str, password: str, rol: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "usuarios", "crear"):
        return no_perm(req)
    db = get_oracle_connection()
    db.create_usuario(id_empleado, username.strip(), password, rol)
    registrar_accion(usuario, "CREAR", "usuarios")
    return RedirectResponse("/usuarios?msg=creado", status_code=303)


def usuarios_editar(req, id_usuario: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "usuarios", "editar"):
        return no_perm(req)

    db = get_oracle_connection()
    u = db.get_usuario(id_usuario)
    if not u:
        return RedirectResponse("/usuarios", status_code=303)

    empleados = db.get_all_empleados()
    roles = ["admin", "mecanico", "facturacion", "readonly"]
    opts_e = [Option(f"{e['nombre']}", value=str(e["id_empleado"]), selected=(e["id_empleado"]==u["id_empleado"])) for e in empleados]

    form = Form(
        Div(
            Div(Label("Empleado"), Select(*opts_e, name="id_empleado", required=True), cls="form-group"),
            Div(Label("Username"), Input(name="username", value=u["username"], required=True), cls="form-group"),
            Div(Label("Nueva contraseña (dejar vacío = no cambiar)"),
                Input(name="password", type="password", placeholder="••••••••", autocomplete="new-password"),
                cls="form-group"),
            Div(Label("Rol"),
                Select(*[Option(r.capitalize(), value=r, selected=(r==u["rol"])) for r in roles],
                       name="rol", required=True),
                cls="form-group"),
            Div(Label("Estado"),
                Select(
                    Option("Activo", value="activo", selected=(u["estado"]=="activo")),
                    Option("Inactivo", value="inactivo", selected=(u["estado"]=="inactivo")),
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


def usuarios_actualizar(req, id_usuario: int, id_empleado: int, username: str,
                         password: str, rol: str, estado: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "usuarios", "editar"):
        return no_perm(req)
    db = get_oracle_connection()
    pw = password if password.strip() else None
    db.update_usuario(id_usuario, username.strip(), rol, estado, pw)
    registrar_accion(usuario, "EDITAR", "usuarios")
    return RedirectResponse("/usuarios?msg=editado", status_code=303)


def usuarios_desactivar(req, id_usuario: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "usuarios", "eliminar"):
        return no_perm(req)
    db = get_oracle_connection()
    u = db.get_usuario(id_usuario)
    if u:
        db.update_usuario(id_usuario, u["username"], u["rol"], "inactivo")
        registrar_accion(usuario, "DESACTIVAR", "usuarios")
    return RedirectResponse("/usuarios?msg=desactivado", status_code=303)
