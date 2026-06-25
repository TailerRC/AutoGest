"""
routes/proveedores.py
=====================
Vista para Proveedores.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout

def render_proveedores_list(req, usuario, proveedores):
    filas = []
    for p in proveedores:
        contacto = p.get("contacto", {})
        lineas = p.get("lineas_productos", [])
        
        acciones = []
        if puede_acceder(usuario, "proveedores", "editar"):
            acciones.append(A("✏️ Editar", href=f"/proveedores/{p['codigoProveedor']}/editar", cls="btn btn-sm btn-blue"))

        filas.append(Tr(
            Td(Span(p.get("codigoProveedor", "—"), cls="font-mono badge badge-gray")),
            Td(Span(p.get("nombreEmpresa", "—"), style="font-weight:600;")),
            Td(Div(*[Span(l, cls="tag") for l in lineas], cls="tag-list") if lineas else "—"),
            Td(
                Div(f"📞 {contacto.get('telefono', '—')}", style="font-size:0.85rem;"),
                Div(f"✉️ {contacto.get('email', '—')}", style="font-size:0.85rem; color:var(--text-muted);")
            ),
            Td(Div(*acciones, cls="flex gap-1") if acciones else "—")
        ))

    crear_btn = A("＋ Nuevo Proveedor", href="/proveedores/nuevo", cls="btn btn-primary") \
        if puede_acceder(usuario, "proveedores", "crear") else ""

    tabla = Div(
        Table(
            Thead(Tr(Th("Código"), Th("Razón Social"), Th("Líneas de Producto"), Th("Contacto"), Th("Acciones"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("No hay proveedores registrados.", colspan="5", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    msg = req.query_params.get("msg", "")
    alert_map = {
        "creado": Div("✅ Proveedor registrado exitosamente.", cls="alert alert-success"),
        "editado": Div("✅ Proveedor actualizado exitosamente.", cls="alert alert-success"),
    }
    alert = alert_map.get(msg, "")

    contenido = Div(
        alert,
        Div(
            Div(H2("🏢 Proveedores"), Span("MongoDB", cls="db-tag mongo"), cls="card-header"),
            Div(
                Div(P("Directorio de proveedores para la cadena de suministro de repuestos.", cls="text-muted text-sm"), crear_btn,
                    cls="flex gap-2", style="justify-content:space-between;align-items:center;margin-bottom:1rem;"),
                tabla,
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Proveedores", "🏢 Gestión de Proveedores", "Base de datos MongoDB", contenido)


def render_proveedores_nuevo(req):
    error = req.query_params.get("error", "")
    alert = Div(f"❌ {error}", cls="alert alert-error") if error else ""

    form = Form(
        alert,
        Div(
            Div(Label("Código del Proveedor"), Input(name="codigo", placeholder="PROV-001", required=True), cls="form-group"),
            Div(Label("Razón Social"), Input(name="nombre_empresa", placeholder="AutoParts S.A.", required=True), cls="form-group"),
            Div(Label("Líneas de Producto (separadas por coma)"), Input(name="lineas_raw", placeholder="Filtros, Lubricantes", required=True), cls="form-group"),
            Div(Label("Teléfono"), Input(name="telefono", placeholder="999888777", required=True), cls="form-group"),
            Div(Label("Correo Electrónico"), Input(name="email", type="email", placeholder="contacto@autoparts.com", required=True), cls="form-group"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/proveedores", cls="btn btn-secondary"),
            Button("💾 Guardar Proveedor", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/proveedores/crear"
    )

    contenido = Div(
        Div(
            Div(H2("➕ Nuevo Proveedor"), A("← Volver", href="/proveedores", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nuevo Proveedor", "➕ Nuevo Proveedor", "", contenido)


def render_proveedores_editar(req, proveedor):
    error = req.query_params.get("error", "")
    alert = Div(f"❌ {error}", cls="alert alert-error") if error else ""

    contacto = proveedor.get("contacto", {})
    lineas = ", ".join(proveedor.get("lineas_productos", []))

    form = Form(
        alert,
        Div(
            Div(Label("Código del Proveedor"), Input(name="codigo", value=proveedor["codigoProveedor"], readonly=True, cls="readonly"), cls="form-group"),
            Div(Label("Razón Social"), Input(name="nombre_empresa", value=proveedor.get("nombreEmpresa", ""), required=True), cls="form-group"),
            Div(Label("Líneas de Producto"), Input(name="lineas_raw", value=lineas, required=True), cls="form-group"),
            Div(Label("Teléfono"), Input(name="telefono", value=contacto.get("telefono", ""), required=True), cls="form-group"),
            Div(Label("Correo Electrónico"), Input(name="email", type="email", value=contacto.get("email", ""), required=True), cls="form-group"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/proveedores", cls="btn btn-secondary"),
            Button("💾 Actualizar Proveedor", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/proveedores/actualizar"
    )

    contenido = Div(
        Div(
            Div(H2(f"✏️ Editar Proveedor: {proveedor['nombreEmpresa']}"), A("← Volver", href="/proveedores", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Editar Proveedor", f"✏️ {proveedor['nombreEmpresa']}", "", contenido)
