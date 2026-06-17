"""
routes/ordenes.py — Órdenes de Trabajo (Oracle simulado)
"""
from fasthtml.common import *
from database import get_oracle_connection
from auth import puede_acceder, registrar_accion
from .helpers import layout, no_perm, badge_estado


def ordenes_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "ver"):
        return no_perm(req)

    db = get_oracle_connection()
    ordenes = db.get_all_ordenes()

    msg = req.query_params.get("msg", "")
    alerts = {
        "creado": Div("✅ Orden creada correctamente.", cls="alert alert-success"),
        "actualizado": Div("✅ Orden actualizada.", cls="alert alert-success"),
        "detalle_agregado": Div("✅ Repuesto agregado a la orden.", cls="alert alert-success"),
    }
    alert = alerts.get(msg, "")

    filas = []
    for o in ordenes:
        acciones = [A("👁️ Ver", href=f"/ordenes/{o['id_orden']}", cls="btn btn-sm btn-secondary")]
        if puede_acceder(usuario, "ordenes", "editar"):
            acciones.append(A("✏️ Editar", href=f"/ordenes/{o['id_orden']}/editar", cls="btn btn-sm btn-blue"))
        filas.append(Tr(
            Td(f"#{o['id_orden']}", cls="font-mono text-muted text-sm"),
            Td(Span(o["placa"], cls="badge badge-gray font-mono")),
            Td(o.get("nombre_cliente", "—")),
            Td(o["nombre_empleado"]),
            Td(o["fecha_ingreso"]),
            Td(o["fecha_entrega"]),
            Td(badge_estado(o["estado"])),
            Td(Div(*acciones, cls="flex gap-1")),
        ))

    # Resumen por estado
    estados = {"pendiente": 0, "en_proceso": 0, "completada": 0}
    for o in ordenes:
        estados[o.get("estado", "pendiente")] = estados.get(o.get("estado", "pendiente"), 0) + 1

    stats = Div(
        Div(Div("⏳", cls="stat-icon yellow"), Div(Div(str(estados["pendiente"]), cls="stat-value"), Div("Pendientes", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div("🔄", cls="stat-icon blue"),   Div(Div(str(estados["en_proceso"]), cls="stat-value"), Div("En Proceso", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div("✅", cls="stat-icon green"),   Div(Div(str(estados["completada"]), cls="stat-value"), Div("Completadas", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div("📋", cls="stat-icon orange"),  Div(Div(str(len(ordenes)), cls="stat-value"), Div("Total", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        cls="stats-grid"
    )

    tabla = Div(
        Table(
            Thead(Tr(Th("#"), Th("Placa"), Th("Cliente"), Th("Mecánico"), Th("Ingreso"), Th("Entrega"), Th("Estado"), Th("Acciones"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("Sin órdenes.", colspan="8", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    crear_btn = A("＋ Nueva Orden", href="/ordenes/nueva", cls="btn btn-primary") \
        if puede_acceder(usuario, "ordenes", "crear") else ""

    contenido = Div(
        alert, stats,
        Div(
            Div(H2("📋 Órdenes de Trabajo"), cls="card-header"),
            Div(
                Div(Span(f"{len(ordenes)} órdenes", cls="text-muted text-sm"), crear_btn,
                    cls="flex gap-2", style="justify-content:space-between;align-items:center;margin-bottom:1rem;"),
                tabla, cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Órdenes", "📋 Órdenes de Trabajo", "Base de datos Oracle", contenido)


def ordenes_detalle(req, id_orden: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "ver"):
        return no_perm(req)

    db = get_oracle_connection()
    o = db.get_orden_detallada(id_orden)
    if not o:
        return RedirectResponse("/ordenes", status_code=303)

    v = o.get("vehiculo") or {}
    e = o.get("empleado") or {}
    c = o.get("cliente") or {}
    detalles = o.get("detalles", [])

    total_repuestos = sum(d["subtotal"] for d in detalles)

    filas_det = []
    for d in detalles:
        filas_det.append(Tr(
            Td(d["nombre_pieza"]),
            Td(str(d["cantidad"])),
            Td(f"S/. {d['precio_unitario']:.2f}"),
            Td(f"S/. {d['subtotal']:.2f}", style="font-weight:600;color:var(--accent)"),
        ))

    # Formulario para agregar repuesto
    agregar_form = ""
    if puede_acceder(usuario, "ordenes", "crear"):
        repuestos = db.get_all_repuestos()
        opts = [Option(f"{r['nombre']} (Stock:{r['stock']})", value=str(r["id_pieza"])) for r in repuestos]
        agregar_form = Div(
            Div(H2("➕ Agregar Repuesto"), cls="card-header"),
            Div(
                Form(
                    Input(type="hidden", name="id_orden", value=str(id_orden)),
                    Div(
                        Div(Label("Repuesto"), Select(*opts, name="id_pieza", required=True), cls="form-group"),
                        Div(Label("Cantidad"), Input(name="cantidad", type="number", min="1", value="1", required=True), cls="form-group"),
                        Div(Label("Precio unitario (S/.)"), Input(name="precio_unitario", type="number", step="0.01", min="0", placeholder="0.00", required=True), cls="form-group"),
                        cls="form-grid"
                    ),
                    Div(Button("➕ Agregar", type="submit", cls="btn btn-primary"), cls="form-actions"),
                    method="post", action="/ordenes/agregar-repuesto"
                ),
                cls="card-body"
            ),
            cls="card mt-2"
        )

    # Cambiar estado
    cambiar_estado = ""
    if puede_acceder(usuario, "ordenes", "editar"):
        estados_opts = [
            Option("Pendiente", value="pendiente", selected=(o["estado"] == "pendiente")),
            Option("En Proceso", value="en_proceso", selected=(o["estado"] == "en_proceso")),
            Option("Completada", value="completada", selected=(o["estado"] == "completada")),
            Option("Cancelada", value="cancelada", selected=(o["estado"] == "cancelada")),
        ]
        cambiar_estado = Form(
            Input(type="hidden", name="id_orden", value=str(id_orden)),
            Div(
                Select(*estados_opts, name="estado", style="width:auto;"),
                Button("Actualizar Estado", type="submit", cls="btn btn-primary btn-sm"),
                cls="flex gap-1", style="align-items:center;"
            ),
            method="post", action="/ordenes/cambiar-estado"
        )

    contenido = Div(
        Div(
            Div(
                H2(f"📋 Orden #{id_orden}"),
                Div(
                    badge_estado(o["estado"]),
                    A("← Volver", href="/ordenes", cls="btn btn-secondary btn-sm"),
                    cls="flex gap-1", style="align-items:center;"
                ),
                cls="card-header"
            ),
            Div(
                Div(
                    Div(Label("Cliente"), Div(c.get("nombre","—"), cls="detail-value"), cls="detail-item"),
                    Div(Label("Vehículo"), Div(f"{v.get('marca','')} {v.get('modelo','')} — {v.get('placa','')}", cls="detail-value"), cls="detail-item"),
                    Div(Label("Mecánico"), Div(e.get("nombre","—"), cls="detail-value"), cls="detail-item"),
                    Div(Label("Fecha Ingreso"), Div(o["fecha_ingreso"], cls="detail-value"), cls="detail-item"),
                    Div(Label("Fecha Entrega"), Div(o["fecha_entrega"], cls="detail-value"), cls="detail-item"),
                    Div(Label("Estado"), Div(cambiar_estado if cambiar_estado else badge_estado(o["estado"]), cls="detail-value"), cls="detail-item"),
                    cls="detail-grid"
                ),
                Div(style="margin-top:1.5rem;"),
                H2("🔧 Repuestos Utilizados", style="font-size:.9rem;font-weight:600;margin-bottom:.75rem;"),
                Div(
                    Table(
                        Thead(Tr(Th("Repuesto"), Th("Cantidad"), Th("Precio Unit."), Th("Subtotal"))),
                        Tbody(*filas_det) if filas_det else Tbody(Tr(Td("Sin repuestos agregados.", colspan="4", cls="no-data"))),
                    ),
                    cls="table-wrap"
                ),
                Div(
                    Span("Total Repuestos:", style="color:var(--text-muted);font-size:.85rem;"),
                    Span(f"S/. {total_repuestos:.2f}", style="font-size:1.2rem;font-weight:700;color:var(--accent);"),
                    cls="flex gap-2 mt-2", style="justify-content:flex-end;align-items:center;"
                ),
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        agregar_form,
        cls="page-body"
    )
    return layout(req, f"Orden #{id_orden}", f"📋 Orden de Trabajo #{id_orden}", c.get("nombre",""), contenido)


def ordenes_nueva(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "crear"):
        return no_perm(req)

    db = get_oracle_connection()
    vehiculos = db.get_all_vehiculos()
    empleados = db.get_all_empleados()
    mecánicos = [e for e in empleados if "mecánic" in e.get("especialidad","").lower()
                 or e.get("cargo","") in ["Jefe de Taller","Mecánico Senior","Mecánico","Electricista Automotriz"]]

    opts_v = [Option(f"{v['placa']} — {v['marca']} {v['modelo']}", value=str(v["id_vehiculo"])) for v in vehiculos]
    opts_e = [Option(f"{e['nombre']} ({e['especialidad']})", value=str(e["id_empleado"])) for e in (mecánicos or empleados)]

    from datetime import date
    hoy = date.today().strftime("%Y-%m-%d")

    form = Form(
        Div(
            Div(Label("Vehículo"), Select(Option("-- Seleccionar --", value=""), *opts_v, name="id_vehiculo", required=True), cls="form-group"),
            Div(Label("Mecánico asignado"), Select(*opts_e, name="id_empleado", required=True), cls="form-group"),
            Div(Label("Fecha de ingreso"), Input(name="fecha_ingreso", type="date", value=hoy, required=True), cls="form-group"),
            Div(Label("Fecha estimada de entrega"), Input(name="fecha_entrega", type="date", required=True), cls="form-group"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/ordenes", cls="btn btn-secondary"),
            Button("💾 Crear Orden", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/ordenes/crear"
    )

    contenido = Div(
        Div(
            Div(H2("📋 Nueva Orden de Trabajo"), A("← Volver", href="/ordenes", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nueva Orden", "📋 Nueva Orden de Trabajo", "", contenido)


def ordenes_crear(req, id_vehiculo: int, id_empleado: int, fecha_ingreso: str, fecha_entrega: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "crear"):
        return no_perm(req)
    db = get_oracle_connection()
    nueva = db.create_orden(id_vehiculo, id_empleado, fecha_ingreso, fecha_entrega)
    registrar_accion(usuario, "CREAR", "ordenes")
    return RedirectResponse(f"/ordenes/{nueva['id_orden']}?msg=creado", status_code=303)


def ordenes_editar(req, id_orden: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "editar"):
        return no_perm(req)

    db = get_oracle_connection()
    o = db.get_orden(id_orden)
    if not o:
        return RedirectResponse("/ordenes", status_code=303)

    vehiculos = db.get_all_vehiculos()
    empleados = db.get_all_empleados()
    opts_v = [Option(f"{v['placa']} — {v['marca']} {v['modelo']}", value=str(v["id_vehiculo"]), selected=(v["id_vehiculo"]==o["id_vehiculo"])) for v in vehiculos]
    opts_e = [Option(f"{e['nombre']}", value=str(e["id_empleado"]), selected=(e["id_empleado"]==o["id_empleado"])) for e in empleados]
    estados_opts = [
        Option("Pendiente", value="pendiente", selected=(o["estado"]=="pendiente")),
        Option("En Proceso", value="en_proceso", selected=(o["estado"]=="en_proceso")),
        Option("Completada", value="completada", selected=(o["estado"]=="completada")),
        Option("Cancelada", value="cancelada", selected=(o["estado"]=="cancelada")),
    ]

    form = Form(
        Div(
            Div(Label("Vehículo"), Select(*opts_v, name="id_vehiculo", required=True), cls="form-group"),
            Div(Label("Mecánico"), Select(*opts_e, name="id_empleado", required=True), cls="form-group"),
            Div(Label("Fecha ingreso"), Input(name="fecha_ingreso", type="date", value=o["fecha_ingreso"], required=True), cls="form-group"),
            Div(Label("Fecha entrega"), Input(name="fecha_entrega", type="date", value=o["fecha_entrega"], required=True), cls="form-group"),
            Div(Label("Estado"), Select(*estados_opts, name="estado", required=True), cls="form-group"),
            cls="form-grid"
        ),
        Input(type="hidden", name="id_orden", value=str(id_orden)),
        Div(
            A("Cancelar", href=f"/ordenes/{id_orden}", cls="btn btn-secondary"),
            Button("💾 Actualizar", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/ordenes/actualizar"
    )

    contenido = Div(
        Div(
            Div(H2(f"✏️ Editar Orden #{id_orden}"), A("← Volver", href=f"/ordenes/{id_orden}", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Editar Orden", f"✏️ Orden #{id_orden}", "", contenido)


def ordenes_actualizar(req, id_orden: int, id_vehiculo: int, id_empleado: int, fecha_ingreso: str, fecha_entrega: str, estado: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "editar"):
        return no_perm(req)
    db = get_oracle_connection()
    db.update_orden(id_orden, id_vehiculo, id_empleado, fecha_ingreso, fecha_entrega, estado)
    registrar_accion(usuario, "EDITAR", "ordenes")
    return RedirectResponse(f"/ordenes/{id_orden}?msg=actualizado", status_code=303)


def ordenes_cambiar_estado(req, id_orden: int, estado: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "editar"):
        return no_perm(req)
    db = get_oracle_connection()
    db.update_orden_estado(id_orden, estado)
    registrar_accion(usuario, "CAMBIAR_ESTADO", "ordenes")
    return RedirectResponse(f"/ordenes/{id_orden}?msg=actualizado", status_code=303)


def ordenes_agregar_repuesto(req, id_orden: int, id_pieza: int, cantidad: int, precio_unitario: float):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "crear"):
        return no_perm(req)
    db = get_oracle_connection()
    db.add_detalle_orden(id_orden, id_pieza, cantidad, precio_unitario)
    registrar_accion(usuario, "AGREGAR_REPUESTO", "ordenes")
    return RedirectResponse(f"/ordenes/{id_orden}?msg=detalle_agregado", status_code=303)
