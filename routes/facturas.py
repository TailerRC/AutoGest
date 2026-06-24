"""
routes/facturas.py — View puro de Facturas
==========================================
Solo renderiza HTML. Lógica en controllers/facturas_ctrl.py.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout, badge_estado, badge_pago

METODOS_PAGO = ["Efectivo", "Tarjeta Débito", "Tarjeta Crédito", "Transferencia"]


def render_facturas_list(req, usuario, facturas):
    """Renderiza la lista de facturas."""
    msg = req.query_params.get("msg", "")
    alert_map = {
        "creado":      Div("✅ Factura generada correctamente.", cls="alert alert-success"),
        "actualizado": Div("✅ Estado de factura actualizado.", cls="alert alert-success"),
    }
    alert = alert_map.get(msg, "")

    total_cobrado  = sum(f["total"] for f in facturas if f["estado_pago"] == "pagada")
    total_pendiente = sum(f["total"] for f in facturas if f["estado_pago"] == "pendiente")

    stats = Div(
        Div(Div("🧾", cls="stat-icon orange"), Div(Div(str(len(facturas)), cls="stat-value"), Div("Total Facturas", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div("✅", cls="stat-icon green"),   Div(Div(f"S/. {total_cobrado:,.2f}", cls="stat-value"), Div("Cobrado", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div("⏳", cls="stat-icon yellow"),  Div(Div(f"S/. {total_pendiente:,.2f}", cls="stat-value"), Div("Por Cobrar", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        cls="stats-grid"
    )

    ids_con_factura = {f["id_orden"] for f in facturas}
    filas = []
    for f in facturas:
        acciones = [A("👁️ Ver", href=f"/facturas/{f['id_factura']}", cls="btn btn-sm btn-secondary")]
        if puede_acceder(usuario, "facturas", "editar") and f["estado_pago"] == "pendiente":
            acciones.append(
                Form(
                    Input(type="hidden", name="id_factura", value=str(f["id_factura"])),
                    Input(type="hidden", name="estado_pago", value="pagada"),
                    Button("💰 Marcar Pagada", type="submit", cls="btn btn-sm btn-success"),
                    method="post", action="/facturas/cambiar-estado"
                )
            )
        filas.append(Tr(
            Td(f"F-{f['id_factura']:04d}", cls="font-mono"),
            Td(f"#{f['id_orden']}"),
            Td(f.get("nombre_cliente", "—")),
            Td(Span(f.get("placa", ""), cls="badge badge-gray font-mono")),
            Td(f["fecha"]),
            Td(f"S/. {f['total']:.2f}", style="font-weight:600;color:var(--accent)"),
            Td(badge_pago(f["metodo_pago"])),
            Td(badge_estado(f["estado_pago"])),
            Td(Div(*acciones, cls="flex gap-1")),
        ))

    crear_btn = A("＋ Generar Factura", href="/facturas/nueva", cls="btn btn-primary") \
        if puede_acceder(usuario, "facturas", "crear") else ""

    tabla = Div(
        Table(
            Thead(Tr(Th("N° Factura"), Th("Orden"), Th("Cliente"), Th("Placa"), Th("Fecha"), Th("Total"), Th("Método"), Th("Estado"), Th("Acciones"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("Sin facturas.", colspan="9", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    contenido = Div(
        alert, stats,
        Div(
            Div(H2("🧾 Facturas"), cls="card-header"),
            Div(
                Div(Span(f"{len(facturas)} facturas", cls="text-muted text-sm"), crear_btn,
                    cls="flex gap-2", style="justify-content:space-between;align-items:center;margin-bottom:1rem;"),
                tabla, cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Facturas", "🧾 Gestión de Facturas", "Base de datos Oracle", contenido)


def render_facturas_nueva(req, ordenes):
    """Renderiza el formulario de nueva factura con órdenes sin facturar."""
    error = req.query_params.get("error", "")
    alert = Div(f"❌ {error}", cls="alert alert-error") if error else ""

    if not ordenes:
        return Div(
            Div("ℹ️ Todas las órdenes ya tienen factura generada.", cls="alert alert-info"),
            A("← Volver a Facturas", href="/facturas", cls="btn btn-secondary"),
        )

    opts_o = [Option(f"Orden #{o['id_orden']} — {o.get('nombre_cliente','?')} ({o['placa']})", value=str(o["id_orden"])) for o in ordenes]

    form = Form(
        alert,
        Div(
            Div(Label("Orden de Trabajo"), Select(*opts_o, name="id_orden", required=True), cls="form-group"),
            Div(Label("Total (S/.)"), Input(name="total", type="number", step="0.01", min="0", placeholder="0.00", required=True), cls="form-group"),
            Div(Label("Método de Pago"),
                Select(*[Option(m, value=m) for m in METODOS_PAGO], name="metodo_pago", required=True),
                cls="form-group"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/facturas", cls="btn btn-secondary"),
            Button("🧾 Generar Factura", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/facturas/crear"
    )

    contenido = Div(
        Div(
            Div(H2("🧾 Generar Nueva Factura"), A("← Volver", href="/facturas", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nueva Factura", "🧾 Generar Factura", "", contenido)


def render_facturas_detalle(req, factura):
    """Renderiza el detalle de una factura."""
    usuario    = req.session.get("usuario")
    id_factura = factura["id_factura"]
    msg = req.query_params.get("msg", "")
    alert = Div("✅ Estado actualizado.", cls="alert alert-success") if msg == "actualizado" else ""

    cambiar_estado = ""
    if puede_acceder(usuario, "facturas", "editar"):
        opts = [
            Option("Pendiente", value="pendiente", selected=(factura["estado_pago"] == "pendiente")),
            Option("Pagada",    value="pagada",    selected=(factura["estado_pago"] == "pagada")),
        ]
        cambiar_estado = Form(
            Input(type="hidden", name="id_factura", value=str(id_factura)),
            Div(Select(*opts, name="estado_pago", style="width:auto;"),
                Button("Actualizar", type="submit", cls="btn btn-primary btn-sm"),
                cls="flex gap-1", style="align-items:center;"),
            method="post", action="/facturas/cambiar-estado"
        )

    contenido = Div(
        alert,
        Div(
            Div(
                Div(
                    H2(f"🧾 Factura F-{id_factura:04d}"),
                    Span("Base de datos Oracle", cls="badge badge-orange"),
                ),
                Div(
                    badge_estado(factura["estado_pago"]),
                    A("← Volver", href="/facturas", cls="btn btn-secondary btn-sm"),
                    cls="flex gap-1", style="align-items:center;"
                ),
                cls="card-header"
            ),
            Div(
                Div(
                    Div(Label("N° Factura"),     Div(f"F-{id_factura:04d}", cls="detail-value font-mono"), cls="detail-item"),
                    Div(Label("Orden"),          Div(f"#{factura['id_orden']}", cls="detail-value"), cls="detail-item"),
                    Div(Label("Fecha"),          Div(factura["fecha"], cls="detail-value"), cls="detail-item"),
                    Div(Label("Total"),          Div(f"S/. {factura['total']:.2f}", cls="detail-value", style="color:var(--accent);font-weight:700;"), cls="detail-item"),
                    Div(Label("Método de Pago"), Div(badge_pago(factura["metodo_pago"]), cls="detail-value"), cls="detail-item"),
                    Div(Label("Estado"),         Div(cambiar_estado if cambiar_estado else badge_estado(factura["estado_pago"]), cls="detail-value"), cls="detail-item"),
                    cls="detail-grid"
                ),
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, f"Factura F-{id_factura:04d}", f"🧾 Factura F-{id_factura:04d}", "", contenido)
