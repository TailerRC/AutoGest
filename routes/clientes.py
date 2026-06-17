"""
routes/clientes.py — CRUD de Clientes (Oracle simulado)
"""
from fasthtml.common import *
from database import get_oracle_connection
from auth import puede_acceder, registrar_accion
from .helpers import layout, no_perm, badge_estado


def clientes_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "clientes", "ver"):
        return no_perm(req)

    db = get_oracle_connection()
    clientes = db.get_all_clientes()
    es_admin = usuario.get("rol") == "admin"

    msg = req.query_params.get("msg", "")
    alert = ""
    if msg == "creado":
        alert = Div("✅ Cliente creado correctamente.", cls="alert alert-success")
    elif msg == "editado":
        alert = Div("✅ Cliente actualizado correctamente.", cls="alert alert-success")
    elif msg == "eliminado":
        alert = Div("🗑️ Cliente eliminado.", cls="alert alert-warning")

    filas = []
    for c in clientes:
        acciones = []
        if puede_acceder(usuario, "clientes", "editar"):
            acciones.append(A("✏️ Editar", href=f"/clientes/{c['id_cliente']}/editar", cls="btn btn-sm btn-blue"))
        if puede_acceder(usuario, "clientes", "eliminar"):
            acciones.append(
                Form(
                    Input(type="hidden", name="id_cliente", value=str(c["id_cliente"])),
                    Button("🗑️", type="submit", cls="btn btn-sm btn-danger",
                           onclick="return confirm('¿Eliminar cliente?')"),
                    method="post", action="/clientes/eliminar"
                )
            )
        filas.append(Tr(
            Td(f"#{c['id_cliente']}", cls="font-mono text-muted text-sm"),
            Td(c["nombre"]),
            Td(c["dni"]),
            Td(c["telefono"]),
            Td(c["email"]),
            Td(Div(*acciones, cls="flex gap-1") if acciones else "—"),
        ))

    tabla = Div(
        Table(
            Thead(Tr(Th("#"), Th("Nombre"), Th("DNI"), Th("Teléfono"), Th("Email"), Th("Acciones"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("No hay clientes registrados.", colspan="6", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    crear_btn = A("＋ Nuevo Cliente", href="/clientes/nuevo", cls="btn btn-primary") \
        if puede_acceder(usuario, "clientes", "crear") else ""

    contenido = Div(
        alert,
        Div(
            Div(H2("👥 Clientes"), cls="card-header"),
            Div(
                Div(
                    Span(f"{len(clientes)} registros", cls="text-muted text-sm"),
                    crear_btn,
                    cls="flex gap-2", style="justify-content:space-between;align-items:center;margin-bottom:1rem;"
                ),
                tabla,
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Clientes", "👥 Gestión de Clientes", "Base de datos Oracle", contenido)


def clientes_nuevo(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "clientes", "crear"):
        return no_perm(req)

    error = req.query_params.get("error", "")
    alert = Div(f"❌ {error}", cls="alert alert-error") if error else ""

    form = Form(
        alert,
        Div(
            Div(Label("Nombre completo"), Input(name="nombre", placeholder="Carlos Mendoza Rivera", required=True), cls="form-group"),
            Div(Label("DNI"), Input(name="dni", placeholder="72345678", maxlength="8", required=True), cls="form-group"),
            Div(Label("Teléfono"), Input(name="telefono", placeholder="987-654-321", required=True), cls="form-group"),
            Div(Label("Email"), Input(name="email", type="email", placeholder="cliente@email.com", required=True), cls="form-group"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/clientes", cls="btn btn-secondary"),
            Button("💾 Guardar Cliente", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/clientes/crear"
    )

    contenido = Div(
        Div(
            Div(
                H2("👤 Nuevo Cliente"),
                A("← Volver", href="/clientes", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nuevo Cliente", "👤 Nuevo Cliente", "Registrar en Oracle", contenido)


def clientes_crear(req, nombre: str, dni: str, telefono: str, email: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "clientes", "crear"):
        return no_perm(req)
    if not nombre or not dni:
        return RedirectResponse("/clientes/nuevo?error=Nombre+y+DNI+son+obligatorios", status_code=303)
    db = get_oracle_connection()
    db.create_cliente(nombre.strip(), telefono.strip(), dni.strip(), email.strip())
    registrar_accion(usuario, "CREAR", "clientes")
    return RedirectResponse("/clientes?msg=creado", status_code=303)


def clientes_editar(req, id_cliente: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "clientes", "editar"):
        return no_perm(req)
    db = get_oracle_connection()
    c = db.get_cliente(id_cliente)
    if not c:
        return RedirectResponse("/clientes", status_code=303)

    form = Form(
        Div(
            Div(Label("Nombre completo"), Input(name="nombre", value=c["nombre"], required=True), cls="form-group"),
            Div(Label("DNI"), Input(name="dni", value=c["dni"], maxlength="8", required=True), cls="form-group"),
            Div(Label("Teléfono"), Input(name="telefono", value=c["telefono"], required=True), cls="form-group"),
            Div(Label("Email"), Input(name="email", type="email", value=c["email"], required=True), cls="form-group"),
            cls="form-grid"
        ),
        Input(type="hidden", name="id_cliente", value=str(id_cliente)),
        Div(
            A("Cancelar", href="/clientes", cls="btn btn-secondary"),
            Button("💾 Actualizar", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/clientes/actualizar"
    )

    contenido = Div(
        Div(
            Div(H2(f"✏️ Editar Cliente #{id_cliente}"),
                A("← Volver", href="/clientes", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Editar Cliente", f"✏️ Editar Cliente #{id_cliente}", "", contenido)


def clientes_actualizar(req, id_cliente: int, nombre: str, dni: str, telefono: str, email: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "clientes", "editar"):
        return no_perm(req)
    db = get_oracle_connection()
    db.update_cliente(id_cliente, nombre.strip(), telefono.strip(), dni.strip(), email.strip())
    registrar_accion(usuario, "EDITAR", "clientes")
    return RedirectResponse("/clientes?msg=editado", status_code=303)


def clientes_eliminar(req, id_cliente: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "clientes", "eliminar"):
        return no_perm(req)
    db = get_oracle_connection()
    db.delete_cliente(id_cliente)
    registrar_accion(usuario, "ELIMINAR", "clientes")
    return RedirectResponse("/clientes?msg=eliminado", status_code=303)
