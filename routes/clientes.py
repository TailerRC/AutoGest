"""
routes/clientes.py — View puro de Clientes
==========================================
Solo contiene funciones de render HTML.
Toda la lógica está en controllers/clientes_ctrl.py y services/clientes_svc.py.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout, no_perm, badge_estado


def render_clientes_list(req, usuario, clientes):
    """Renderiza la lista de clientes."""
    msg = req.query_params.get("msg", "")
    alert_map = {
        "creado":    Div("✅ Cliente creado correctamente.", cls="alert alert-success"),
        "editado":   Div("✅ Cliente actualizado correctamente.", cls="alert alert-success"),
        "eliminado": Div("🗑️ Cliente eliminado.", cls="alert alert-warning"),
    }
    alert = alert_map.get(msg, "")

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


def render_clientes_nuevo(req):
    """Renderiza el formulario de nuevo cliente."""
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


def render_clientes_editar(req, cliente):
    """Renderiza el formulario de edición de un cliente existente."""
    id_cliente = cliente["id_cliente"]
    form = Form(
        Div(
            Div(Label("Nombre completo"), Input(name="nombre", value=cliente["nombre"], required=True), cls="form-group"),
            Div(Label("DNI"), Input(name="dni", value=cliente["dni"], maxlength="8", required=True), cls="form-group"),
            Div(Label("Teléfono"), Input(name="telefono", value=cliente["telefono"], required=True), cls="form-group"),
            Div(Label("Email"), Input(name="email", type="email", value=cliente["email"], required=True), cls="form-group"),
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
