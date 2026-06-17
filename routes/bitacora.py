"""
routes/bitacora.py — Bitácora de Diagnóstico (MongoDB simulado)
"""
from fasthtml.common import *
from database import get_oracle_connection, get_mongo_connection
from auth import puede_acceder, registrar_accion
from .helpers import layout, no_perm, badge_estado


def bitacora_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "bitacora", "ver"):
        return no_perm(req)

    mongo = get_mongo_connection()
    db = get_oracle_connection()
    bitacoras = mongo.get_all_bitacoras()

    msg = req.query_params.get("msg", "")
    alert = Div("✅ Bitácora registrada correctamente.", cls="alert alert-success") if msg == "creada" else ""

    filas = []
    for b in bitacoras:
        sintomas_tags = Div(*[Span(s, cls="tag") for s in b.get("sintomas", [])], cls="tag-list")
        codigos = b.get("codigos_obd", [])
        codigos_tags = Div(*[Span(c, cls="tag-obd") for c in codigos], cls="tag-list") if codigos else Span("—", cls="text-muted")
        orden = db.get_orden(b["id_orden_ref"])
        placa = ""
        if orden:
            v = db.get_vehiculo(orden["id_vehiculo"])
            placa = v["placa"] if v else ""

        filas.append(Tr(
            Td(f"#{b['id_orden_ref']}" + (f" — {placa}" if placa else ""), cls="font-mono text-sm"),
            Td(b["fecha"]),
            Td(b["mecanico"]),
            Td(sintomas_tags),
            Td(codigos_tags),
            Td(A("👁️ Ver", href=f"/bitacora/{b['id_orden_ref']}", cls="btn btn-sm btn-secondary")),
        ))

    crear_btn = A("＋ Nueva Bitácora", href="/bitacora/nueva", cls="btn btn-primary") \
        if puede_acceder(usuario, "bitacora", "crear") else ""

    tabla = Div(
        Table(
            Thead(Tr(Th("Orden"), Th("Fecha"), Th("Mecánico"), Th("Síntomas"), Th("Códigos OBD"), Th("Acciones"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("Sin bitácoras.", colspan="6", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    contenido = Div(
        alert,
        Div(
            Div(H2("📝 Bitácora de Diagnóstico"), Span("MongoDB", cls="db-tag mongo"), cls="card-header"),
            Div(
                Div(Span(f"{len(bitacoras)} registros", cls="text-muted text-sm"), crear_btn,
                    cls="flex gap-2", style="justify-content:space-between;align-items:center;margin-bottom:1rem;"),
                tabla, cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Bitácora", "📝 Bitácora de Diagnóstico", "Base de datos MongoDB", contenido)


def bitacora_detalle(req, id_orden: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "bitacora", "ver"):
        return no_perm(req)

    mongo = get_mongo_connection()
    db = get_oracle_connection()
    b = mongo.get_bitacora_by_orden(id_orden)

    if not b:
        return RedirectResponse(f"/bitacora?no_encontrado={id_orden}", status_code=303)

    orden = db.get_orden_detallada(id_orden)
    cliente = orden.get("cliente") or {} if orden else {}
    vehiculo = orden.get("vehiculo") or {} if orden else {}

    sintomas = b.get("sintomas", [])
    codigos = b.get("codigos_obd", [])
    fotos = b.get("fotos", [])

    contenido = Div(
        Div(
            Div(
                Div(
                    H2(f"📝 Bitácora — Orden #{id_orden}"),
                    Span("MongoDB", cls="db-tag mongo"),
                ),
                A("← Volver", href="/bitacora", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(
                Div(
                    Div(Label("Orden de referencia"), Div(f"#{id_orden}", cls="detail-value font-mono"), cls="detail-item"),
                    Div(Label("Fecha diagnóstico"), Div(b.get("fecha","—"), cls="detail-value"), cls="detail-item"),
                    Div(Label("Mecánico"), Div(b.get("mecanico","—"), cls="detail-value"), cls="detail-item"),
                    Div(Label("Cliente"), Div(cliente.get("nombre","—"), cls="detail-value"), cls="detail-item"),
                    Div(Label("Vehículo"), Div(f"{vehiculo.get('marca','')} {vehiculo.get('modelo','')} — {vehiculo.get('placa','')}", cls="detail-value"), cls="detail-item"),
                    Div(Label("Mano de obra (S/.)"), Div(f"S/. {b.get('mano_de_obra',0):.2f}", cls="detail-value", style="color:var(--accent);font-weight:700;"), cls="detail-item"),
                    cls="detail-grid"
                ),
                Div(style="margin-top:1.5rem;"),
                Div(
                    Div(
                        Div(
                            Span("🩺 Síntomas reportados", style="font-size:.75rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;"),
                            Div(*[Span(s, cls="tag") for s in sintomas], cls="tag-list mt-1") if sintomas else P("Sin síntomas.", cls="text-muted text-sm mt-1"),
                            style="margin-bottom:1.25rem;"
                        ),
                        Div(
                            Span("🔴 Códigos OBD detectados", style="font-size:.75rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;"),
                            Div(*[Span(c, cls="tag-obd") for c in codigos], cls="tag-list mt-1") if codigos else P("Sin códigos OBD.", cls="text-muted text-sm mt-1"),
                            style="margin-bottom:1.25rem;"
                        ),
                        Div(
                            Span("📋 Hallazgos y diagnóstico", style="font-size:.75rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;"),
                            P(b.get("hallazgos","—"), style="margin-top:.5rem;color:var(--text-secondary);font-size:.875rem;line-height:1.6;"),
                        ),
                    ),
                ),
                Div(style="margin-top:1rem;"),
                Div(
                    Span("📷 Fotos adjuntas", style="font-size:.75rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;"),
                    Div(*[Span(f"🖼️ {foto}", cls="tag") for foto in fotos], cls="tag-list mt-1") if fotos else P("Sin fotos.", cls="text-muted text-sm mt-1"),
                ),
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, f"Bitácora #{id_orden}", f"📝 Bitácora de Diagnóstico #{id_orden}", "", contenido)


def bitacora_nueva(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "bitacora", "crear"):
        return no_perm(req)

    db = get_oracle_connection()
    mongo = get_mongo_connection()
    ordenes = db.get_all_ordenes()
    ids_con_bit = {b["id_orden_ref"] for b in mongo.get_all_bitacoras()}
    ordenes_disp = [o for o in ordenes if o["id_orden"] not in ids_con_bit]

    empleados = db.get_all_empleados()
    mecanicos = [e for e in empleados if "mecán" in e.get("especialidad","").lower() or
                 e.get("cargo","") in ["Jefe de Taller","Mecánico Senior","Mecánico","Electricista Automotriz"]]

    opts_o = [Option(f"Orden #{o['id_orden']} — {o.get('nombre_cliente','?')} / {o['placa']}", value=str(o["id_orden"])) for o in ordenes_disp]
    opts_m = [Option(f"{e['nombre']}", value=e["nombre"]) for e in (mecanicos or empleados)]

    form = Form(
        Div(
            Div(Label("Orden de Trabajo"),
                Select(Option("-- Seleccionar --", value=""), *opts_o, name="id_orden", required=True),
                cls="form-group"),
            Div(Label("Mecánico responsable"),
                Select(*opts_m, name="mecanico", required=True),
                cls="form-group"),
            Div(Label("Mano de obra (S/.)"),
                Input(name="mano_de_obra", type="number", step="0.01", min="0", placeholder="0.00", required=True),
                cls="form-group"),
            cls="form-grid"
        ),
        Div(
            Div(Label("Síntomas reportados (uno por línea)"),
                Textarea(name="sintomas", placeholder="Motor hace ruido\nVibración al frenar\nCheck engine encendido", rows="4", required=True),
                cls="form-group full-width"),
            Div(Label("Códigos OBD detectados (separados por coma, dejar vacío si no aplica)"),
                Input(name="codigos_obd", placeholder="P0300, C0031"),
                cls="form-group full-width"),
            Div(Label("Hallazgos y diagnóstico detallado"),
                Textarea(name="hallazgos", placeholder="Descripción detallada del diagnóstico...", rows="5", required=True),
                cls="form-group full-width"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/bitacora", cls="btn btn-secondary"),
            Button("💾 Guardar Bitácora", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/bitacora/crear"
    )

    contenido = Div(
        Div(
            Div(
                Div(H2("📝 Nueva Bitácora de Diagnóstico"), Span("MongoDB", cls="db-tag mongo")),
                A("← Volver", href="/bitacora", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nueva Bitácora", "📝 Nueva Bitácora", "Guardar en MongoDB", contenido)


def bitacora_crear(req, id_orden: int, mecanico: str, sintomas: str,
                   codigos_obd: str, hallazgos: str, mano_de_obra: float):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "bitacora", "crear"):
        return no_perm(req)

    mongo = get_mongo_connection()
    lista_sintomas = [s.strip() for s in sintomas.split("\n") if s.strip()]
    lista_codigos = [c.strip() for c in codigos_obd.split(",") if c.strip()] if codigos_obd else []

    mongo.create_bitacora(id_orden, mecanico.strip(), lista_sintomas, lista_codigos, hallazgos.strip(), mano_de_obra)
    registrar_accion(usuario, "CREAR", "bitacora")
    return RedirectResponse("/bitacora?msg=creada", status_code=303)
