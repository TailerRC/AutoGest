"""
routes/cotizaciones.py
======================
Vista para Cotizaciones.
"""
import json
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout, badge_estado

def render_cotizaciones_list(req, usuario, cotizaciones):
    filas = []
    for c in cotizaciones:
        servicios = c.get("servicios_repuestos", [])
        items = Ul(*[Li(f"{s.get('descripcion')} - S/. {float(s.get('precio',0)):.2f}") for s in servicios], style="padding-left:1.2rem; font-size:0.85rem; color:var(--text-secondary);")
        
        estado_badge = badge_estado("Vigente" if c.get("vigente", False) else "Vencida")

        filas.append(Tr(
            Td(Span(c.get("codigoCotizacion", "—"), cls="font-mono badge badge-gray")),
            Td(c.get("cliente_str", "—")),
            Td(c.get("vehiculo_str", "—")),
            Td(c.get("fecha_validez", "—")),
            Td(estado_badge),
            Td(items),
            Td(f"S/. {c.get('total', 0):.2f}", style="font-weight:700; color:var(--accent);"),
            Td(A("👁️ Ver", href=f"/cotizaciones/{c['codigoCotizacion']}", cls="btn btn-sm btn-secondary"))
        ))

    crear_btn = A("＋ Nueva Cotización", href="/cotizaciones/nueva", cls="btn btn-primary") \
        if puede_acceder(usuario, "cotizaciones", "crear") else ""

    tabla = Div(
        Table(
            Thead(Tr(Th("Código"), Th("Cliente"), Th("Vehículo"), Th("Válido Hasta"), Th("Estado"), Th("Items"), Th("Total"), Th("Acciones"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("No hay cotizaciones registradas.", colspan="8", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    msg = req.query_params.get("msg", "")
    alert = Div("✅ Cotización generada exitosamente.", cls="alert alert-success") if msg == "creado" else ""

    contenido = Div(
        alert,
        Div(
            Div(H2("📝 Cotizaciones"), Span("MongoDB", cls="db-tag mongo"), cls="card-header"),
            Div(
                Div(P("Gestión de proformas y cotizaciones pre-servicio.", cls="text-muted text-sm"), crear_btn,
                    cls="flex gap-2", style="justify-content:space-between;align-items:center;margin-bottom:1rem;"),
                tabla,
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Cotizaciones", "📝 Gestión de Cotizaciones", "Base de datos MongoDB", contenido)


def render_cotizaciones_nueva(req, clientes, vehiculos):
    error = req.query_params.get("error", "")
    alert = Div(f"❌ {error}", cls="alert alert-error") if error else ""

    opts_c = [Option(f"{c['nombre']} ({c['dni']})", value=str(c["id_cliente"])) for c in clientes]
    opts_v = [Option(f"#{v['id_vehiculo']} — {v.get('marca','')} {v.get('modelo','')} ({v.get('placa','')})", value=str(v["id_vehiculo"])) for v in vehiculos]

    # Para el formulario simplificamos "servicios" a un string JSON oculto que el usuario llenaría 
    # (en una app real habría JS para agregar filas dinámicamente)
    
    js_script = Script("""
        function actualizarJSON() {
            const desc = document.getElementById('desc_item').value;
            const precio = document.getElementById('precio_item').value;
            if(desc && precio) {
                const arr = [{descripcion: desc, precio: parseFloat(precio)}];
                document.getElementById('items_json').value = JSON.stringify(arr);
                document.getElementById('total').value = precio;
            }
        }
    """)

    form = Form(
        alert,
        js_script,
        Div(
            Div(Label("Cliente"), Select(Option("-- Seleccionar --", value=""), *opts_c, name="id_cliente", required=True), cls="form-group"),
            Div(Label("Vehículo"), Select(Option("-- Seleccionar --", value=""), *opts_v, name="id_vehiculo", required=True), cls="form-group"),
            Div(Label("Fecha de Validez"), Input(name="fecha_validez", type="date", required=True), cls="form-group"),
            cls="form-grid"
        ),
        H3("Ítem de Cotización (Simplificado)", style="font-size:1rem; margin-top:1rem;"),
        Div(
            Div(Label("Descripción del Servicio/Repuesto"), Input(id="desc_item", placeholder="Cambio de aceite", required=True, oninput="actualizarJSON()"), cls="form-group"),
            Div(Label("Precio (S/.)"), Input(id="precio_item", type="number", min="0", step="0.01", required=True, oninput="actualizarJSON()"), cls="form-group"),
            cls="form-grid"
        ),
        Input(type="hidden", name="items_json", id="items_json", value="[]"),
        Input(type="hidden", name="total", id="total", value="0"),
        Div(
            A("Cancelar", href="/cotizaciones", cls="btn btn-secondary"),
            Button("💾 Generar Cotización", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/cotizaciones/crear"
    )

    contenido = Div(
        Div(
            Div(H2("📝 Nueva Cotización"), A("← Volver", href="/cotizaciones", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nueva Cotización", "📝 Nueva Cotización", "", contenido)


def render_cotizaciones_detalle(req, cotizacion):
    if not cotizacion:
        return RedirectResponse("/cotizaciones", status_code=303)

    servicios = cotizacion.get("servicios_repuestos", [])
    filas_items = [
        Tr(Td(s.get("descripcion", "—")), Td(f"S/. {float(s.get('precio', 0)):.2f}"))
        for s in servicios
    ]

    contenido = Div(
        Div(
            Div(
                Div(
                    H2(f"📝 Cotización {cotizacion.get('codigoCotizacion')}"),
                    Span("MongoDB", cls="db-tag mongo"),
                ),
                A("← Volver", href="/cotizaciones", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(
                Div(
                    Div(Label("Cliente"), Div(cotizacion.get("cliente_str", "—"), cls="detail-value"), cls="detail-item"),
                    Div(Label("Vehículo"), Div(cotizacion.get("vehiculo_str", "—"), cls="detail-value"), cls="detail-item"),
                    Div(Label("Válida Hasta"), Div(cotizacion.get("fecha_validez", "—"), cls="detail-value"), cls="detail-item"),
                    cls="detail-grid"
                ),
                Div(style="margin-top:1.5rem;"),
                H3("Detalle de Ítems", style="font-size:1rem; margin-bottom:0.5rem;"),
                Table(
                    Thead(Tr(Th("Descripción"), Th("Precio"))),
                    Tbody(*filas_items) if filas_items else Tbody(Tr(Td("Sin ítems.", colspan="2", cls="no-data"))),
                    cls="table-wrap"
                ),
                Div(
                    Span("Total:", cls="text-muted"),
                    Span(f"S/. {cotizacion.get('total', 0):.2f}", style="font-size:1.2rem;font-weight:700;color:var(--accent); margin-left:0.5rem;"),
                    style="margin-top:1rem; text-align:right;"
                ),
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, f"Cotización {cotizacion.get('codigoCotizacion')}", "📝 Detalle de Cotización", "", contenido)
