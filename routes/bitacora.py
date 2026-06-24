"""
routes/bitacora.py — View puro de Bitácora de Diagnóstico
=========================================================
Solo renderiza HTML. Lógica en controllers/bitacora_ctrl.py.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout

def render_bitacora_list(req, usuario, bitacoras):
    """Renderiza la lista de bitácoras de diagnóstico."""
    msg = req.query_params.get("msg", "")
    alert = Div("✅ Bitácora registrada correctamente.", cls="alert alert-success") \
        if msg == "creado" else ""

    filas = []
    for b in bitacoras:
        sintomas_tags = Div(*[Span(s, cls="tag") for s in b.get("sintomas", [])], cls="tag-list")
        codigos = b.get("codigo_OBD", [])
        codigos_tags = Div(*[Span(c, cls="tag-obd") for c in codigos], cls="tag-list") \
            if codigos else Span("—", cls="text-muted")

        id_vehiculo = b.get("idVehiculo", "?")

        filas.append(Tr(
            Td(f"Vehículo #{id_vehiculo}", cls="font-mono text-sm"),
            Td(str(b.get("idEmpleado", "—"))),
            Td(sintomas_tags),
            Td(codigos_tags),
            Td(A("👁️ Ver", href=f"/bitacora/{id_vehiculo}", cls="btn btn-sm btn-secondary")),
        ))

    crear_btn = A("＋ Nueva Bitácora", href="/bitacora/nueva", cls="btn btn-primary") \
        if puede_acceder(usuario, "bitacora", "crear") else ""

    tabla = Div(
        Table(
            Thead(Tr(Th("Vehículo"), Th("ID Empleado"), Th("Síntomas"), Th("Códigos OBD"), Th("Acciones"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("Sin bitácoras.", colspan="5", cls="no-data"))),
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


def render_bitacora_detalle(req, bitacora, vehiculo):
    """Renderiza el detalle de una bitácora."""
    if not bitacora:
        from fasthtml.common import RedirectResponse
        return RedirectResponse("/bitacora", status_code=303)

    id_vehiculo = bitacora.get("idVehiculo", "?")
    vehiculo_desc = f"{vehiculo.get('marca','')} {vehiculo.get('modelo','')} — {vehiculo.get('placa','')}" if vehiculo else "—"
    sintomas = bitacora.get("sintomas", [])
    codigos  = bitacora.get("codigo_OBD", [])
    fotos    = bitacora.get("fotografias_url", [])

    contenido = Div(
        Div(
            Div(
                Div(
                    H2(f"📝 Bitácora — Vehículo #{id_vehiculo}"),
                    Span("MongoDB", cls="db-tag mongo"),
                ),
                A("← Volver", href="/bitacora", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(
                Div(
                    Div(Label("Vehículo Referencia"),    Div(f"#{id_vehiculo}", cls="detail-value font-mono"), cls="detail-item"),
                    Div(Label("ID Empleado"),            Div(str(bitacora.get("idEmpleado", "—")), cls="detail-value"), cls="detail-item"),
                    Div(Label("Cod. Especificación"),    Div(bitacora.get("codigoEspecificacion", "—"), cls="detail-value"), cls="detail-item"),
                    Div(Label("Vehículo Datos"),         Div(vehiculo_desc, cls="detail-value"), cls="detail-item"),
                    cls="detail-grid"
                ),
                Div(style="margin-top:1.5rem;"),
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
                        Span("📋 Observaciones", style="font-size:.75rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;"),
                        P(bitacora.get("observaciones", "—"), style="margin-top:.5rem;color:var(--text-secondary);font-size:.875rem;line-height:1.6;"),
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
    return layout(req, f"Bitácora #{id_vehiculo}", f"📝 Bitácora de Diagnóstico #{id_vehiculo}", "", contenido)


def render_bitacora_nueva(req, vehiculos):
    """Renderiza el formulario de nueva bitácora."""
    error = req.query_params.get("error", "")
    alert = Div(f"❌ {error}", cls="alert alert-error") if error else ""

    opts_v = [Option(f"Vehículo #{v['id_vehiculo']} — {v.get('marca','?')} {v.get('modelo','')} / {v.get('placa','')}", value=str(v["id_vehiculo"])) for v in vehiculos]

    form = Form(
        alert,
        Div(
            Div(Label("Vehículo"),
                Select(Option("-- Seleccionar --", value=""), *opts_v, name="id_vehiculo", required=True),
                cls="form-group"),
            Div(Label("ID Empleado responsable"),
                Input(name="id_empleado", type="number", placeholder="1", required=True),
                cls="form-group"),
            Div(Label("Código Especificación"),
                Input(name="codigo_especificacion", placeholder="ESP-TOY-001", required=True),
                cls="form-group"),
            cls="form-grid"
        ),
        Div(
            Div(Label("Síntomas reportados (separados por coma)"),
                Input(name="sintomas", placeholder="Motor hace ruido, Vibración al frenar", required=True),
                cls="form-group full-width"),
            Div(Label("Códigos OBD detectados (separados por coma, dejar vacío si no aplica)"),
                Input(name="codigos_obd", placeholder="P0300, C0031"),
                cls="form-group full-width"),
            Div(Label("Observaciones"),
                Textarea(name="observaciones", placeholder="Observaciones detalladas del diagnóstico...", rows="5", required=True),
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
