"""
routes/facturas.py — Gestión de Facturas (Oracle simulado)
"""
from fasthtml.common import *
from database import get_oracle_connection
from auth import puede_acceder, registrar_accion
from .helpers import layout, no_perm, badge_estado, badge_pago


def facturas_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "facturas", "ver"):
        return no_perm(req)

    db = get_oracle_connection()
    facturas = db.get_all_facturas()

    msg = req.query_params.get("msg", "")
    alerts = {
        "creada":     Div("✅ Factura generada correctamente.", cls="alert alert-success"),
        "actualizada": Div("✅ Estado de factura actualizado.", cls="alert alert-success"),
    }
    alert = alerts.get(msg, "")

    total_cobrado = sum(f["total"] for f in facturas if f["estado_pago"] == "pagada")
    total_pendiente = sum(f["total"] for f in facturas if f["estado_pago"] == "pendiente")

    stats = Div(
        Div(Div("🧾", cls="stat-icon orange"), Div(Div(str(len(facturas)), cls="stat-value"), Div("Total Facturas", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div("✅", cls="stat-icon green"),   Div(Div(f"S/. {total_cobrado:,.2f}", cls="stat-value"), Div("Cobrado", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div("⏳", cls="stat-icon yellow"),  Div(Div(f"S/. {total_pendiente:,.2f}", cls="stat-value"), Div("Por Cobrar", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        cls="stats-grid"
    )

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
            Td(Span(f.get("placa",""), cls="badge badge-gray font-mono")),
            Td(f["fecha"]),
            Td(f"S/. {f['total']:.2f}", style="font-weight:600;color:var(--accent)"),
            Td(badge_pago(f["metodo_pago"])),
            Td(badge_estado(f["estado_pago"])),
            Td(Div(*acciones, cls="flex gap-1")),
        ))

    # Botón nueva factura solo si hay órdenes sin facturar
    ordenes_sin_factura = []
    todas_ordenes = db.get_all_ordenes()
    ids_con_factura = {f["id_orden"] for f in facturas}
    ordenes_sin_factura = [o for o in todas_ordenes if o["id_orden"] not in ids_con_factura]

    crear_btn = A("＋ Generar Factura", href="/facturas/nueva", cls="btn btn-primary") \
        if puede_acceder(usuario, "facturas", "crear") and ordenes_sin_factura else ""

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


def facturas_detalle(req, id_factura: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "facturas", "ver"):
        return no_perm(req)

    db = get_oracle_connection()
    f = db.get_factura(id_factura)
    if not f:
        return RedirectResponse("/facturas", status_code=303)

    o = db.get_orden_detallada(f["id_orden"])
    detalles = o.get("detalles", []) if o else []
    cliente = o.get("cliente") or {}
    vehiculo = o.get("vehiculo") or {}

    filas = [Tr(Td(d["nombre_pieza"]), Td(str(d["cantidad"])),
                Td(f"S/. {d['precio_unitario']:.2f}"), Td(f"S/. {d['subtotal']:.2f}"))
             for d in detalles]

    cambiar_estado = ""
    if puede_acceder(usuario, "facturas", "editar"):
        opts = [
            Option("Pendiente", value="pendiente", selected=(f["estado_pago"]=="pendiente")),
            Option("Pagada", value="pagada", selected=(f["estado_pago"]=="pagada")),
        ]
        cambiar_estado = Form(
            Input(type="hidden", name="id_factura", value=str(id_factura)),
            Div(Select(*opts, name="estado_pago", style="width:auto;"),
                Button("Actualizar", type="submit", cls="btn btn-primary btn-sm"),
                cls="flex gap-1", style="align-items:center;"),
            method="post", action="/facturas/cambiar-estado"
        )

    contenido = Div(
        Div(
            Div(
                Div(
                    H2(f"🧾 Factura F-{id_factura:04d}"),
                    Span("Base de datos Oracle", cls="badge badge-orange"),
                ),
                Div(
                    badge_estado(f["estado_pago"]),
                    A("← Volver", href="/facturas", cls="btn btn-secondary btn-sm"),
                    cls="flex gap-1", style="align-items:center;"
                ),
                cls="card-header"
            ),
            Div(
                Div(
                    Div(Label("N° Factura"), Div(f"F-{id_factura:04d}", cls="detail-value font-mono"), cls="detail-item"),
                    Div(Label("Orden de Trabajo"), Div(f"#{f['id_orden']}", cls="detail-value"), cls="detail-item"),
                    Div(Label("Cliente"), Div(cliente.get("nombre","—"), cls="detail-value"), cls="detail-item"),
                    Div(Label("Vehículo"), Div(f"{vehiculo.get('placa','')} — {vehiculo.get('marca','')} {vehiculo.get('modelo','')}", cls="detail-value"), cls="detail-item"),
                    Div(Label("Fecha"), Div(f["fecha"], cls="detail-value"), cls="detail-item"),
                    Div(Label("Método de Pago"), Div(badge_pago(f["metodo_pago"]), cls="detail-value"), cls="detail-item"),
                    Div(Label("Estado de Pago"), Div(cambiar_estado if cambiar_estado else badge_estado(f["estado_pago"]), cls="detail-value"), cls="detail-item"),
                    cls="detail-grid"
                ),
                Div(style="margin-top:1.5rem;"),
                H2("Detalle de Repuestos", style="font-size:.9rem;font-weight:600;margin-bottom:.75rem;"),
                Div(
                    Table(
                        Thead(Tr(Th("Repuesto"), Th("Cant."), Th("Precio Unit."), Th("Subtotal"))),
                        Tbody(*filas) if filas else Tbody(Tr(Td("Sin repuestos.", colspan="4", cls="no-data"))),
                    ),
                    cls="table-wrap"
                ),
                Div(
                    Span("TOTAL:", style="font-size:.85rem;color:var(--text-muted);font-weight:600;"),
                    Span(f"S/. {f['total']:.2f}", style="font-size:1.5rem;font-weight:700;color:var(--accent);"),
                    cls="flex gap-2 mt-2", style="justify-content:flex-end;align-items:center;"
                ),
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, f"Factura F-{id_factura:04d}", f"🧾 Factura F-{id_factura:04d}", cliente.get("nombre",""), contenido)


def facturas_nueva(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "facturas", "crear"):
        return no_perm(req)

    db = get_oracle_connection()
    todas_ordenes = db.get_all_ordenes()
    ids_con_factura = {f["id_orden"] for f in db.get_all_facturas()}
    ordenes_sin_factura = [o for o in todas_ordenes if o["id_orden"] not in ids_con_factura]

    if not ordenes_sin_factura:
        return Div(
            Div("ℹ️ Todas las órdenes ya tienen factura generada.", cls="alert alert-info"),
            A("← Volver a Facturas", href="/facturas", cls="btn btn-secondary"),
        )

    opts_o = [Option(f"Orden #{o['id_orden']} — {o.get('nombre_cliente','?')} ({o['placa']})", value=str(o["id_orden"])) for o in ordenes_sin_factura]
    metodos = ["Efectivo", "Tarjeta Débito", "Tarjeta Crédito", "Transferencia", "Cheque"]

    form = Form(
        Div(
            Div(Label("Orden de Trabajo"), Select(*opts_o, name="id_orden", required=True), cls="form-group"),
            Div(Label("Total (S/.)"), Input(name="total", type="number", step="0.01", min="0", placeholder="0.00", required=True), cls="form-group"),
            Div(Label("Método de Pago"),
                Select(*[Option(m, value=m) for m in metodos], name="metodo_pago", required=True),
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


def facturas_crear(req, id_orden: int, total: float, metodo_pago: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "facturas", "crear"):
        return no_perm(req)
    db = get_oracle_connection()
    nueva = db.create_factura(id_orden, total, metodo_pago)
    registrar_accion(usuario, "CREAR", "facturas")
    return RedirectResponse(f"/facturas/{nueva['id_factura']}?msg=creada", status_code=303)


def facturas_cambiar_estado(req, id_factura: int, estado_pago: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "facturas", "editar"):
        return no_perm(req)
    db = get_oracle_connection()
    db.update_factura_estado(id_factura, estado_pago)
    registrar_accion(usuario, "EDITAR", "facturas")
    return RedirectResponse(f"/facturas/{id_factura}?msg=actualizada", status_code=303)
