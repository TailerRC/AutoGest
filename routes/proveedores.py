"""
routes/proveedores.py
=====================
Vista para Proveedores.
"""
from fasthtml.common import *
from .helpers import layout

def render_proveedores_list(req, proveedores):
    filas = []
    for p in proveedores:
        contacto = p.get("contacto", {})
        lineas = p.get("lineas_productos", [])
        
        filas.append(Tr(
            Td(Span(p.get("codigoProveedor", "—"), cls="font-mono badge badge-gray")),
            Td(Span(p.get("nombreEmpresa", "—"), style="font-weight:600;")),
            Td(Div(*[Span(l, cls="tag") for l in lineas], cls="tag-list") if lineas else "—"),
            Td(
                Div(f"📞 {contacto.get('telefono', '—')}", style="font-size:0.85rem;"),
                Div(f"✉️ {contacto.get('email', '—')}", style="font-size:0.85rem; color:var(--text-muted);")
            )
        ))

    tabla = Div(
        Table(
            Thead(Tr(Th("Código"), Th("Razón Social"), Th("Líneas de Producto"), Th("Contacto"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("No hay proveedores registrados.", colspan="4", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    contenido = Div(
        Div(
            Div(H2("🏢 Proveedores"), Span("MongoDB", cls="db-tag mongo"), cls="card-header"),
            Div(
                P("Directorio de proveedores para la cadena de suministro de repuestos.", cls="text-muted text-sm", style="margin-bottom:1rem;"),
                tabla,
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Proveedores", "🏢 Gestión de Proveedores", "Base de datos MongoDB", contenido)
