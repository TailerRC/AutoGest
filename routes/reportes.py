"""
routes/reportes.py — View puro de Reportes
==========================================
Solo renderiza HTML. Lógica en controllers/reportes_ctrl.py.
"""
from fasthtml.common import *
from .helpers import layout, badge_estado, badge_pago


def render_reportes_list(req, ordenes, logs, resumen):
    """Renderiza la pantalla principal de reportes (Dashboard)."""
    # Selector de orden para reporte detallado
    opts_o = [
        Option(f"Orden #{o['id_orden']} — {o.get('nombre_cliente','?')} / {o['placa']} ({o['estado']})",
               value=str(o["id_orden"]))
        for o in ordenes
    ]

    selector = Form(
        Div(
            Div(Label("Seleccionar Orden de Trabajo"),
                Select(*opts_o, name="id_orden", required=True, id="orden_selector"),
                cls="form-group"),
            cls="form-grid"
        ),
        Div(Button("📊 Ver Reporte Completo", type="submit", cls="btn btn-primary"), cls="mt-1"),
        method="get", action="/reportes/detalle"
    )

    stats = Div(
        Div(Div("📋", cls="stat-icon orange"), Div(Div(str(resumen["total_ordenes"]), cls="stat-value"), Div("Órdenes Totales", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div("🧾", cls="stat-icon blue"),   Div(Div(str(resumen["total_facturas"]), cls="stat-value"), Div("Facturas Emitidas", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div("📝", cls="stat-icon green"),  Div(Div(str(resumen["total_bitacoras"]), cls="stat-value"), Div("Bitácoras", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div("🔔", cls="stat-icon yellow"), Div(Div(str(resumen["alertas_activas"]), cls="stat-value"), Div("Alertas Activas", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        cls="stats-grid"
    )

    # Log de actividad reciente
    filas_log = []
    for log in logs:
        resultado_badge = Span("✅ Exitoso", cls="badge badge-green")  # El nuevo mock no tiene "resultado"
        filas_log.append(Tr(
            Td(log.get("fecha_hora", ""), cls="font-mono text-sm"),
            Td(f"Emp/Usr #{log.get('idUsuario', '?')}", cls="text-muted text-sm"),
            Td(Span(log.get("accion", ""), style="font-weight:600;")),
            Td(Span(log.get("entidad_afectada", ""), cls="badge badge-purple")),
            Td(resultado_badge),
        ))

    tabla_log = Div(
        Table(
            Thead(Tr(Th("Fecha/Hora"), Th("Empleado"), Th("Acción"), Th("Módulo"), Th("Resultado"))),
            Tbody(*filas_log) if filas_log else Tbody(Tr(Td("Sin registros.", colspan="5", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    contenido = Div(
        stats,
        Div(
            Div(
                Div(H2("📊 Reporte Combinado Oracle + MongoDB"), Span("Oracle + MongoDB", cls="badge badge-orange")),
                cls="card-header"
            ),
            Div(selector, cls="card-body"),
            cls="card mb-2"
        ),
        Div(
            Div(H2("📜 Log de Actividad Reciente"), Span("MongoDB", cls="db-tag mongo"), cls="card-header"),
            Div(tabla_log, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Reportes", "📊 Reportes del Sistema", "Datos combinados Oracle + MongoDB", contenido)


def render_reportes_detalle(req, datos):
    """Renderiza el reporte detallado de una orden integrando Oracle y Mongo."""
    orden       = datos["orden"]
    id_orden    = orden["id_orden"]
    cliente     = datos["cliente"]
    vehiculo    = datos["vehiculo"]
    empleado    = datos["empleado"]
    detalles    = datos["detalles"]
    factura     = datos["factura"]
    bitacora    = datos["bitacora"]
    esp_tecnica = datos["esp_tecnica"]
    total_rep   = datos["total_rep"]
    mano_obra   = datos["mano_obra"]
    gran_total  = datos["gran_total"]

    # ── Bloque Oracle ────────────────────────────────────────────────
    filas_rep = [
        Tr(Td(d["nombre_pieza"]), Td(str(d["cantidad"])),
           Td(f"S/. {d['precio_unitario']:.2f}"), Td(f"S/. {d['subtotal']:.2f}"))
        for d in detalles
    ]

    seccion_oracle = Div(
        Div(
            H2("📋 Datos de la Orden de Trabajo"),
            Span("Base de datos Oracle (Relacional)", cls="db-tag oracle"),
            style="display:flex;align-items:center;gap:.75rem;margin-bottom:1rem;"
        ),
        Div(
            Div(Label("N° Orden"), Div(f"#{id_orden}", cls="detail-value font-mono"), cls="detail-item"),
            Div(Label("Cliente"), Div(cliente.get("nombre", "—"), cls="detail-value"), cls="detail-item"),
            Div(Label("DNI"), Div(cliente.get("dni", "—"), cls="detail-value"), cls="detail-item"),
            Div(Label("Vehículo"), Div(f"{vehiculo.get('marca','')} {vehiculo.get('modelo','')} {vehiculo.get('año','')}", cls="detail-value"), cls="detail-item"),
            Div(Label("Placa"), Div(Span(vehiculo.get("placa", "—"), cls="badge badge-gray font-mono"), cls="detail-value"), cls="detail-item"),
            Div(Label("Mecánico"), Div(empleado.get("nombre", "—"), cls="detail-value"), cls="detail-item"),
            Div(Label("Ingreso"), Div(orden.get("fecha_ingreso", "—"), cls="detail-value"), cls="detail-item"),
            Div(Label("Entrega"), Div(orden.get("fecha_entrega", "—"), cls="detail-value"), cls="detail-item"),
            Div(Label("Estado Orden"), Div(badge_estado(orden.get("estado", "pendiente")), cls="detail-value"), cls="detail-item"),
            cls="detail-grid"
        ),
        Div(style="margin-top:1.25rem;"),
        H2("Repuestos Utilizados", style="font-size:.85rem;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:.6rem;"),
        Div(
            Table(
                Thead(Tr(Th("Repuesto"), Th("Cant."), Th("Precio Unit."), Th("Subtotal"))),
                Tbody(*filas_rep) if filas_rep else Tbody(Tr(Td("Sin repuestos.", colspan="4", cls="no-data"))),
            ),
            cls="table-wrap"
        ),
        Div(style="margin-top:1rem;"),
        Div(
            Span("Total Repuestos:", cls="text-muted text-sm"),
            Span(f"S/. {total_rep:.2f}", style="font-size:1.1rem;font-weight:700;color:var(--accent);"),
            cls="flex gap-2", style="justify-content:flex-end;align-items:center;"
        ),
        # Factura
        Div(
            Div(
                Div(Label("N° Factura"), Div(f"F-{factura['id_factura']:04d}" if factura else "Sin factura", cls="detail-value"), cls="detail-item"),
                Div(Label("Total Facturado"), Div(f"S/. {factura['total']:.2f}" if factura else "—", cls="detail-value", style="color:var(--accent);font-weight:700;"), cls="detail-item"),
                Div(Label("Método de Pago"), Div(badge_pago(factura["metodo_pago"]) if factura else "—", cls="detail-value"), cls="detail-item"),
                Div(Label("Estado de Pago"), Div(badge_estado(factura["estado_pago"]) if factura else "—", cls="detail-value"), cls="detail-item"),
                cls="detail-grid"
            ),
            style="margin-top:1.25rem;padding-top:1.25rem;border-top:1px solid var(--border);"
        ),
        cls="card-body"
    )

    # ── Bloque MongoDB — Bitácora ─────────────────────────────────────
    if bitacora:
        sintomas = bitacora.get("sintomas", [])
        codigos = bitacora.get("codigo_OBD", [])
        seccion_mongo_bit = Div(
            Div(
                H2("📝 Bitácora de Diagnóstico"),
                Span("Base de datos MongoDB (Documental)", cls="db-tag mongo"),
                style="display:flex;align-items:center;gap:.75rem;margin-bottom:1rem;"
            ),
            Div(
                Div(Label("Cod Diagnóstico"), Div(bitacora.get("codigoDiagnostico", "—"), cls="detail-value font-mono"), cls="detail-item"),
                Div(Label("Emp ID"), Div(str(bitacora.get("idEmpleado", "—")), cls="detail-value"), cls="detail-item"),
                Div(Label("Cod Especificación"), Div(bitacora.get("codigoEspecificacion", "—"), cls="detail-value font-mono"), cls="detail-item"),
                cls="detail-grid"
            ),
            Div(style="margin-top:1rem;"),
            Div(
                Span("🩺 Síntomas (Array MongoDB)", style="font-size:.72rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;"),
                Div(*[Span(s, cls="tag") for s in sintomas], cls="tag-list mt-1") if sintomas else P("—", cls="text-muted text-sm mt-1"),
                style="margin-bottom:1rem;"
            ),
            Div(
                Span("🔴 Códigos OBD (Array MongoDB)", style="font-size:.72rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;"),
                Div(*[Span(c, cls="tag-obd") for c in codigos], cls="tag-list mt-1") if codigos else P("Sin códigos OBD.", cls="text-muted text-sm mt-1"),
                style="margin-bottom:1rem;"
            ),
            Div(
                Span("📋 Observaciones", style="font-size:.72rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;"),
                P(bitacora.get("observaciones", "—"), style="margin-top:.4rem;color:var(--text-secondary);font-size:.875rem;line-height:1.6;"),
            ),
        )
    else:
        seccion_mongo_bit = Div(
            Div(
                H2("📝 Bitácora de Diagnóstico"),
                Span("MongoDB", cls="db-tag mongo"),
                style="display:flex;align-items:center;gap:.75rem;margin-bottom:1rem;"
            ),
            Div("⚠️ Esta orden no tiene bitácora de diagnóstico registrada en MongoDB.", cls="alert alert-warning"),
        )

    if esp_tecnica:
        det_tec = esp_tecnica.get("detalles_tecnicos", {})
        seccion_mongo_esp = Div(
            Div(
                H2("📚 Especificaciones Técnicas del Vehículo"),
                Span("Base de datos MongoDB (Documental)", cls="db-tag mongo"),
                style="display:flex;align-items:center;gap:.75rem;margin-bottom:1rem;"
            ),
            Div(
                Div(Label("Cod Especificación"), Div(esp_tecnica.get("codigoEspecificacion", "—"), cls="detail-value font-mono"), cls="detail-item"),
                Div(Label("Marca / Modelo"), Div(f"{esp_tecnica.get('marca','?')} / {esp_tecnica.get('modelo','?')}", cls="detail-value"), cls="detail-item"),
                Div(Label("Motor"), Div(det_tec.get("motor", "—"), cls="detail-value"), cls="detail-item"),
                Div(Label("Aceite recomendado"), Div(det_tec.get("aceite", "—"), cls="detail-value"), cls="detail-item"),
                Div(Label("Transmisión"), Div(det_tec.get("transmision", "—"), cls="detail-value"), cls="detail-item"),
                Div(Label("Batería / Bujías"), Div(f"{det_tec.get('batería','?')} {det_tec.get('bujias','')}", cls="detail-value"), cls="detail-item"),
                cls="detail-grid"
            )
        )
    else:
        seccion_mongo_esp = Div(
            P("ℹ️ No se encontraron especificaciones técnicas en el catálogo MongoDB para este vehículo.", cls="text-muted text-sm")
        )

    # ── Resumen de costos ─────────────────────────────────────────────
    resumen = Div(
        Div(
            Div(H2("💰 Resumen de Costos"), Span("Oracle + MongoDB", cls="badge badge-orange"), cls="card-header"),
            Div(
                Div(
                    Div(Label("Repuestos (Oracle — DETALLE_ORDEN_REPUESTOS)"), Div(f"S/. {total_rep:.2f}", cls="detail-value"), cls="detail-item"),
                    Div(Label("Mano de obra (MongoDB — bitacora_diagnostico)"), Div(f"S/. {mano_obra:.2f}", cls="detail-value"), cls="detail-item"),
                    Div(Label("GRAN TOTAL"), Div(f"S/. {gran_total:.2f}", cls="detail-value", style="font-size:1.3rem;font-weight:700;color:var(--accent);"), cls="detail-item"),
                    cls="detail-grid"
                ),
                cls="card-body"
            ),
            cls="card"
        ),
        style="margin-top:1rem;"
    )

    contenido = Div(
        Div(
            Div(
                H2(f"📊 Reporte Integrado — Orden #{id_orden}"),
                Div(
                    Span("Oracle + MongoDB", cls="badge badge-orange"),
                    A("← Volver a Reportes", href="/reportes", cls="btn btn-secondary btn-sm"),
                    cls="flex gap-1", style="align-items:center;"
                ),
                cls="card-header"
            ),
            Div(
                P("Este reporte combina datos relacionales de Oracle con documentos de MongoDB, usando ",
                  Strong("id_vehiculo"), " como campo puente entre ambas bases de datos.", cls="text-muted text-sm"),
                cls="card-body"
            ),
            cls="card mb-2"
        ),
        # Oracle section
        Div(
            Div(
                Div(H2("🔴 Fuente: Oracle Database (Relacional)"), cls="card-header"),
                seccion_oracle,
                cls="card fade-in mb-2"
            )
        ),
        # MongoDB sections
        Div(
            Div(
                Div(H2("🟢 Fuente: MongoDB (Documental)"), cls="card-header"),
                Div(seccion_mongo_bit, Div(style="border-top:1px solid var(--border);margin:1.25rem 0;"),
                    seccion_mongo_esp, cls="card-body"),
                cls="card fade-in mb-2"
            )
        ),
        resumen,
        cls="page-body"
    )
    return layout(req, f"Reporte Orden #{id_orden}", f"📊 Reporte Integrado — Orden #{id_orden}",
                  "Oracle + MongoDB", contenido)
