"""
routes/cotizaciones.py
======================
Vista para Cotizaciones.
"""
from fasthtml.common import *
from .helpers import layout

def render_cotizaciones_list(req, cotizaciones):
    filas = []
    for c in cotizaciones:
        servicios = c.get("servicios_repuestos", [])
        # Renderizamos los items como lista
        items = Ul(*[Li(f"{s.get('descripcion')} (Cant: {s.get('cantidad',1)}) - S/. {s.get('subtotal',0):.2f}") for s in servicios], style="padding-left:1.2rem; font-size:0.85rem; color:var(--text-secondary);")
        
        filas.append(Tr(
            Td(Span(c.get("codigoCotizacion", "—"), cls="font-mono badge badge-gray")),
            Td(c.get("cliente_str", "—")),
            Td(c.get("vehiculo_str", "—")),
            Td(c.get("fecha_validez", "—")),
            Td(items),
            Td(f"S/. {c.get('total', 0):.2f}", style="font-weight:700; color:var(--accent);")
        ))

    tabla = Div(
        Table(
            Thead(Tr(Th("Código"), Th("Cliente (Oracle)"), Th("Vehículo (Oracle)"), Th("Válido Hasta"), Th("Items"), Th("Total"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("No hay cotizaciones registradas.", colspan="6", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    contenido = Div(
        Div(
            Div(H2("📝 Cotizaciones"), Span("MongoDB", cls="db-tag mongo"), cls="card-header"),
            Div(
                P("Gestión de proformas y cotizaciones pre-servicio.", cls="text-muted text-sm", style="margin-bottom:1rem;"),
                tabla,
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Cotizaciones", "📝 Gestión de Cotizaciones", "Base de datos MongoDB", contenido)
