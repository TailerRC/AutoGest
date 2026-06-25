"""
routes/historial.py
===================
Vista para Historial de Mantenimiento.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout, badge_estado

def render_historial_list(req, usuario, historiales):
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

    crear_btn = A("＋ Nuevo Registro", href="/historial/nuevo", cls="btn btn-primary") \
        if puede_acceder(usuario, "historial", "crear") else ""

    tabla = Div(
        Table(
            Thead(Tr(Th("Vehículo (Oracle)"), Th("Kilometraje"), Th("Fecha Servicio"), Th("Diagnósticos"), Th("Estado"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("No hay registros en el historial.", colspan="5", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    msg = req.query_params.get("msg", "")
    alert = Div("✅ Registro añadido.", cls="alert alert-success") if msg == "creado" else ""

    contenido = Div(
        alert,
        Div(
            Div(H2("🗂️ Historial de Mantenimiento"), Span("MongoDB", cls="db-tag mongo"), cls="card-header"),
            Div(
                Div(P("Colección que almacena el recorrido histórico de un vehículo.", cls="text-muted text-sm"), crear_btn,
                    cls="flex gap-2", style="justify-content:space-between;align-items:center;margin-bottom:1rem;"),
                tabla,
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Historial", "🗂️ Historial de Mantenimiento", "Base de datos MongoDB", contenido)


def render_historial_nuevo(req, vehiculos):
    error = req.query_params.get("error", "")
    alert = Div(f"❌ {error}", cls="alert alert-error") if error else ""

    opts_v = [Option(f"#{v['id_vehiculo']} — {v.get('marca','')} {v.get('modelo','')} ({v.get('placa','')})", value=str(v["id_vehiculo"])) for v in vehiculos]

    form = Form(
        alert,
        Div(
            Div(Label("Vehículo"), Select(Option("-- Seleccionar --", value=""), *opts_v, name="id_vehiculo", required=True), cls="form-group"),
            Div(Label("Kilometraje de Ingreso"), Input(name="kilometraje_ingreso", type="number", min="0", placeholder="50000", required=True), cls="form-group"),
            Div(Label("Fecha de Servicio"), Input(name="fecha_servicio", type="date", required=True), cls="form-group"),
            Div(Label("Estado Final"), 
                Select(
                    Option("Completada", value="completada"),
                    Option("En Proceso", value="en_proceso"),
                    Option("Pendiente", value="pendiente"),
                    name="estado_final", required=True
                ), 
                cls="form-group"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/historial", cls="btn btn-secondary"),
            Button("💾 Guardar Registro", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/historial/crear"
    )

    contenido = Div(
        Div(
            Div(H2("➕ Nuevo Registro de Historial"), A("← Volver", href="/historial", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nuevo Historial", "➕ Nuevo Registro de Historial", "", contenido)
