"""
routes/historial.py
===================
Vista para Historial de Mantenimiento.
"""
from fasthtml.common import *
from .helpers import layout, badge_estado

def render_historial_list(req, historiales):
    filas = []
    for h in historiales:
        diagnosticos = h.get("diagnosticos_asociados", [])
        filas.append(Tr(
            Td(Span(h.get("vehiculo_str", "—"), style="font-weight:600;")),
            Td(f"{h.get('kilometraje_ingreso', 0):,} km"),
            Td(h.get("fecha_servicio", "—")),
            Td(Div(*[Span(d, cls="tag-obd") for d in diagnosticos], cls="tag-list") if diagnosticos else "—"),
            Td(badge_estado(h.get("estado_final", "pendiente")))
        ))

    tabla = Div(
        Table(
            Thead(Tr(Th("Vehículo (Oracle)"), Th("Kilometraje"), Th("Fecha Servicio"), Th("Diagnósticos"), Th("Estado"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("No hay registros en el historial.", colspan="5", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    contenido = Div(
        Div(
            Div(H2("🗂️ Historial de Mantenimiento"), Span("MongoDB", cls="db-tag mongo"), cls="card-header"),
            Div(
                P("Colección que almacena el recorrido histórico de un vehículo, relacionándolo con sus diagnósticos de bitácora.", cls="text-muted text-sm", style="margin-bottom:1rem;"),
                tabla,
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Historial", "🗂️ Historial de Mantenimiento", "Base de datos MongoDB", contenido)
