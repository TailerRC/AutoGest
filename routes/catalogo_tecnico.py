"""
routes/catalogo_tecnico.py — View puro del Catálogo Técnico
===========================================================
Solo renderiza HTML. Lógica en controllers/catalogo_ctrl.py.
"""
from fasthtml.common import *
from .helpers import layout


def render_catalogo_list(req, catalogo):
    """Renderiza el catálogo de especificaciones técnicas MongoDB."""
    marca  = req.query_params.get("marca", "")
    modelo = req.query_params.get("modelo", "")
    año_s  = req.query_params.get("año", "")

    busqueda = Form(
        Div(
            Div(Label("Marca"),  Input(name="marca",  value=marca,  placeholder="Toyota, Kia..."), cls="form-group"),
            Div(Label("Modelo"), Input(name="modelo", value=modelo, placeholder="Corolla, Rio..."), cls="form-group"),
            Div(Label("Año"),    Input(name="año",    type="number", value=año_s, placeholder="2020", min="1990", max="2030"), cls="form-group"),
            cls="form-grid"
        ),
        Div(
            Button("🔍 Buscar", type="submit", cls="btn btn-primary"),
            A("✖ Limpiar", href="/catalogo", cls="btn btn-secondary"),
            cls="flex gap-1 mt-1"
        ),
        method="get", action="/catalogo"
    )

    cards = []
    for esp in catalogo:
        det_tec = esp.get("detalles_tecnicos", {})

        cards.append(
            Div(
                Div(
                    Div(
                        Span("🔧", style="font-size:1.4rem;"),
                        Div(
                            Div(f"{esp['marca']} {esp['modelo']}", style="font-weight:700;font-size:1rem;"),
                            Div(str(esp["anio"]), cls="badge badge-blue", style="margin-top:.2rem;"),
                        ),
                    ),
                    Span("MongoDB", cls="db-tag mongo"),
                    cls="card-header"
                ),
                Div(
                    Div(
                        Div(Label("Cod Especificación"), Div(esp.get("codigoEspecificacion", "—"), cls="detail-value font-mono"), cls="detail-item"),
                        Div(Label("Motor"),               Div(det_tec.get("motor", "—"), cls="detail-value"), cls="detail-item"),
                        Div(Label("Aceite recomendado"),  Div(det_tec.get("aceite", "—"), cls="detail-value"), cls="detail-item"),
                        Div(Label("Transmisión"),         Div(det_tec.get("transmision", "—"), cls="detail-value"), cls="detail-item"),
                        Div(Label("Bujías / Batería"),    Div(f"{det_tec.get('bujias','')} {det_tec.get('batería','')}", cls="detail-value"), cls="detail-item"),
                        cls="detail-grid"
                    ),
                    cls="card-body"
                ),
                cls="card fade-in", style="margin-bottom:1rem;"
            )
        )

    no_results = Div("🔍 No se encontraron especificaciones para los criterios de búsqueda.", cls="no-data") \
        if not catalogo else ""

    contenido = Div(
        Div(
            Div(H2("📚 Catálogo Técnico"), Span("MongoDB", cls="db-tag mongo"), cls="card-header"),
            Div(busqueda, cls="card-body"),
            cls="card mb-2"
        ),
        Div(
            Span(f"📊 {len(catalogo)} resultado(s)", cls="text-muted text-sm", style="margin-bottom:.75rem;display:block;"),
            *cards,
            no_results,
        ),
        cls="page-body"
    )
    return layout(req, "Catálogo Técnico", "📚 Catálogo de Especificaciones", "Base de datos MongoDB", contenido)
