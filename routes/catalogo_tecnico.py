"""
routes/catalogo_tecnico.py — Catálogo de Especificaciones Técnicas (MongoDB simulado)
"""
from fasthtml.common import *
from database import get_mongo_connection
from auth import puede_acceder
from .helpers import layout, no_perm


def catalogo_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "catalogo", "ver"):
        return no_perm(req)

    mongo = get_mongo_connection()

    # Parámetros de búsqueda
    marca = req.query_params.get("marca", "").strip()
    modelo = req.query_params.get("modelo", "").strip()
    anio_str = req.query_params.get("anio", "").strip()
    anio = int(anio_str) if anio_str.isdigit() else None

    resultados = mongo.buscar_catalogo(marca=marca, modelo=modelo, año=anio)

    # Formulario de búsqueda
    busqueda = Form(
        Div(
            Div(Label("Marca"), Input(name="marca", value=marca, placeholder="Toyota, Kia..."), cls="form-group"),
            Div(Label("Modelo"), Input(name="modelo", value=modelo, placeholder="Corolla, Rio..."), cls="form-group"),
            Div(Label("Año"), Input(name="anio", type="number", value=anio_str, placeholder="2020", min="1990", max="2030"), cls="form-group"),
            cls="form-grid"
        ),
        Div(
            Button("🔍 Buscar", type="submit", cls="btn btn-primary"),
            A("✖ Limpiar", href="/catalogo", cls="btn btn-secondary"),
            cls="flex gap-1 mt-1"
        ),
        method="get", action="/catalogo"
    )

    # Tarjetas de resultados
    cards = []
    for esp in resultados:
        presion = esp.get("presion_neumaticos", {})
        frenos = esp.get("tipo_frenos", {})
        notas = esp.get("notas_tecnicas", [])

        cards.append(
            Div(
                Div(
                    Div(
                        Span("🔧", style="font-size:1.4rem;"),
                        Div(
                            Div(f"{esp['marca']} {esp['modelo']}", style="font-weight:700;font-size:1rem;"),
                            Div(str(esp["año"]), cls="badge badge-blue", style="margin-top:.2rem;"),
                        ),
                    ),
                    Span("MongoDB", cls="db-tag mongo"),
                    cls="card-header"
                ),
                Div(
                    Div(
                        Div(Label("Motor"), Div(esp.get("tipo_motor","—"), cls="detail-value"), cls="detail-item"),
                        Div(Label("Aceite recomendado"), Div(esp.get("tipo_aceite","—"), cls="detail-value"), cls="detail-item"),
                        Div(Label("Capacidad aceite"), Div(f"{esp.get('capacidad_aceite_L','?')} L", cls="detail-value"), cls="detail-item"),
                        Div(Label("Presión neumáticos"), Div(f"Del: {presion.get('delantera','?')} / Tra: {presion.get('trasera','?')}", cls="detail-value"), cls="detail-item"),
                        Div(Label("Frenos delantero"), Div(frenos.get("delantero","—"), cls="detail-value"), cls="detail-item"),
                        Div(Label("Frenos trasero"), Div(frenos.get("trasero","—"), cls="detail-value"), cls="detail-item"),
                        cls="detail-grid"
                    ),
                    Div(style="margin-top:1rem;"),
                    Div(
                        Span("📝 Notas técnicas:", style="font-size:.75rem;font-weight:600;color:var(--text-muted);text-transform:uppercase;"),
                        Ul(*[Li(n, style="color:var(--text-secondary);font-size:.82rem;margin-top:.3rem;") for n in notas],
                           style="margin-top:.4rem;padding-left:1.2rem;"),
                    ) if notas else "",
                    cls="card-body"
                ),
                cls="card fade-in", style="margin-bottom:1rem;"
            )
        )

    no_results = Div("🔍 No se encontraron especificaciones para los criterios de búsqueda.", cls="no-data") \
        if not resultados else ""

    contenido = Div(
        Div(
            Div(H2("📚 Catálogo Técnico"), Span("MongoDB", cls="db-tag mongo"), cls="card-header"),
            Div(busqueda, cls="card-body"),
            cls="card mb-2"
        ),
        Div(
            Span(f"📊 {len(resultados)} resultado(s)", cls="text-muted text-sm", style="margin-bottom:.75rem;display:block;"),
            *cards,
            no_results,
        ),
        cls="page-body"
    )
    return layout(req, "Catálogo Técnico", "📚 Catálogo de Especificaciones", "Base de datos MongoDB", contenido)
