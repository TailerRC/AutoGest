"""
routes/reportes.py — View puro de Reportes
==========================================
Solo renderiza HTML. Lógica en controllers/reportes_ctrl.py.
"""
from fasthtml.common import *
from .helpers import layout, badge_estado, badge_pago
import json as _json


def render_reportes_list(req, ordenes, logs, resumen, mecanicos, usuarios=None):
    """Renderiza la pantalla principal de reportes."""

    usuarios = usuarios or []
    mapa_usuario = {u["id_empleado"]: u["username"] for u in usuarios}

    # Paginación mecánicos
    try:
        page_mec = int(req.query_params.get("page_mec", 1))
        if page_mec < 1:
            page_mec = 1
    except ValueError:
        page_mec = 1

    limit_mec = 10
    total_mec = len(mecanicos)
    total_pages_mec = max(1, (total_mec + limit_mec - 1) // limit_mec)
    if page_mec > total_pages_mec:
        page_mec = total_pages_mec
    mec_pag = mecanicos[(page_mec - 1) * limit_mec: page_mec * limit_mec]

    # Selector órdenes — solo orden + empleado, sin estado
    opts_o = [
        Option(f"Orden #{o['id_orden']} — {o.get('nombre_cliente','?')} / {o['placa']}",
               value=str(o["id_orden"]))
        for o in ordenes
    ]

    # Stats
    stats_data = [
        ("fa-solid fa-clipboard-list", resumen["total_ordenes"],   "Órdenes Totales",   "orange"),
        ("fa-solid fa-file-invoice",   resumen["total_facturas"],  "Facturas Emitidas", "blue"),
        ("fa-solid fa-book-open",      resumen["total_bitacoras"], "Bitácoras",          "green"),
        ("fa-solid fa-bell",           resumen["alertas_activas"], "Alertas Activas",   "yellow"),
    ]
    stats = Div(
        *[
            Div(
                Div(I(cls=icon), cls=f"stat-icon {color}"),
                Div(Div(str(val), cls="stat-value"), Div(label, cls="stat-label"), cls="stat-info"),
                cls="stat-card"
            )
            for icon, val, label, color in stats_data
        ],
        cls="stats-grid"
    )

    # Datos para gráfico de barras (Chart.js)
    chart_labels = _json.dumps(["Órdenes", "Facturas", "Bitácoras", "Alertas"])
    chart_values = _json.dumps([
        resumen["total_ordenes"],
        resumen["total_facturas"],
        resumen["total_bitacoras"],
        resumen["alertas_activas"],
    ])

    grafico = Div(
        Script(src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"),
        Canvas(id="chartResumen", style="width:100%;height:220px;"),
        Script(f"""
        (function() {{
            function initChart() {{
                if (typeof Chart === 'undefined') {{ setTimeout(initChart, 100); return; }}
                new Chart(document.getElementById('chartResumen'), {{
                    type: 'bar',
                    data: {{
                        labels: {chart_labels},
                        datasets: [{{
                            label: 'Total',
                            data: {chart_values},
                            backgroundColor: ['#F59E0B','#3B82F6','#10B981','#EF4444'],
                            borderRadius: 6,
                            borderWidth: 0,
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ display: false }} }},
                        scales: {{
                            y: {{ beginAtZero: true, grid: {{ color: 'rgba(0,0,0,0.05)' }} }},
                            x: {{ grid: {{ display: false }} }}
                        }}
                    }}
                }});
            }}
            initChart();
        }})();
        """),
        style="position:relative;height:240px;width:600px;"
    )

    selector_form = Form(
        Div(
            Label(I(cls="fa-solid fa-clipboard-list"), " Seleccionar Orden de Trabajo",
                  style="font-size:.75rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:.5rem;"),
            Select(*opts_o, name="id_orden", required=True,
                   style="width:100%;margin-bottom:1rem;"),
            Button(I(cls="fa-solid fa-chart-bar"), " Ver Reporte Completo",
                   type="submit", cls="btn btn-primary"),
        ),
        method="get", action="/reportes/detalle"
    )

    # Sección superior: dos columnas separadas por línea
    seccion_superior = Div(
        Div(
            H3(I(cls="fa-solid fa-chart-bar"), " Resumen General",
               style="font-size:.8rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:1rem;"),
            grafico,
            style="flex:1;padding-right:1.5rem;border-right:1.5px solid var(--border);"
        ),
        Div(
            H3(I(cls="fa-solid fa-magnifying-glass-chart"), " Reporte por Orden",
               style="font-size:.8rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:1rem;"),
            selector_form,
            style="flex:1;padding-left:1.5rem;"
        ),
        style="display:flex;align-items:flex-start;gap:0;"
    )

    # Tabla mecánicos con paginación
    filas_mecanicos = [
        Tr(
            Td(m["nombre"]),
            Td(m["especialidad"]),
            Td(str(m["ordenes_atendidas"])),
            Td(str(m["completadas"]), cls="text-green"),
            Td(str(m["en_proceso"]), cls="text-orange"),
            Td(f"S/. {m.get('facturado_total') or 0:.2f}", style="font-weight:600;")
        )
        for m in mec_pag
    ]

    # Paginación mecánicos
    pag_mec_prev = A(I(cls="fa-solid fa-chevron-left"), " Anterior",
                     href=f"/reportes?page_mec={page_mec-1}", cls="btn btn-sm btn-secondary") \
        if page_mec > 1 else \
        Span(I(cls="fa-solid fa-chevron-left"), " Anterior",
             cls="btn btn-sm btn-secondary disabled", style="opacity:0.5;cursor:not-allowed;")

    pag_mec_next = A("Siguiente ", I(cls="fa-solid fa-chevron-right"),
                     href=f"/reportes?page_mec={page_mec+1}", cls="btn btn-sm btn-secondary") \
        if page_mec < total_pages_mec else \
        Span("Siguiente ", I(cls="fa-solid fa-chevron-right"),
             cls="btn btn-sm btn-secondary disabled", style="opacity:0.5;cursor:not-allowed;")

    pag_mec_nums = [
        A(str(p), href=f"/reportes?page_mec={p}",
          cls="btn btn-sm btn-primary" if p == page_mec else "btn btn-sm btn-secondary",
          style="min-width:32px;text-align:center;")
        for p in range(1, total_pages_mec + 1)
    ]

    tabla_mecanicos = Div(
        Div(
            Table(
                Thead(Tr(Th("Mecánico"), Th("Especialidad"), Th("Órdenes"), Th("Completadas"), Th("En Proceso"), Th("Total Facturado"))),
                Tbody(*filas_mecanicos) if filas_mecanicos else Tbody(Tr(Td("Sin registros.", colspan="6", cls="no-data"))),
            ),
            cls="table-wrap"
        ),
        Div(
            Span(f"Mostrando {(page_mec-1)*limit_mec+1}–{min(page_mec*limit_mec, total_mec)} de {total_mec}",
                 cls="text-muted text-sm"),
            Div(pag_mec_prev, *pag_mec_nums, pag_mec_next, cls="paginacion-nav"),
            cls="paginacion-container"
        )
    )

    # Log — hora Lima (UTC-5) y username
    from datetime import datetime, timezone, timedelta
    lima_tz = timezone(timedelta(hours=-5))

    def fmt_lima(fecha_str):
        try:
            dt = datetime.fromisoformat(str(fecha_str))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(lima_tz).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(fecha_str)

    filas_log = []
    for log in logs:
        id_emp = log.get("idUsuario")
        username = mapa_usuario.get(id_emp, f"#{id_emp}")
        filas_log.append(Tr(
            Td(fmt_lima(log.get("fecha_hora", "")), cls="font-mono text-sm"),
            Td(username, cls="text-muted text-sm"),
            Td(Span(log.get("accion", ""), style="font-weight:600;")),
            Td(Span(log.get("entidad_afectada", ""), cls="badge badge-purple")),
            Td(Span(I(cls="fa-solid fa-circle-check"), " Exitoso", cls="badge badge-green")),
        ))

    tabla_log = Div(
        Div(
            Table(
                Thead(Tr(Th("Fecha/Hora"), Th("Usuario"), Th("Acción"), Th("Módulo"), Th("Resultado"))),
                Tbody(*filas_log) if filas_log else Tbody(Tr(Td("Sin registros.", colspan="5", cls="no-data"))),
            ),
            style="max-height:280px;overflow-y:auto;overflow-x:auto;"
        ),
        cls="table-wrap"
    )

    contenido = Div(
        Div(
            Div(
                Div(H2(I(cls="fa-solid fa-chart-pie"), " Resumen del Sistema"),
                    Span("Oracle + MongoDB", cls="badge badge-orange"),
                    cls="card-header"),
                Div(seccion_superior, cls="card-body"),
                cls="card mb-2"
            )
        ),
        Div(
            Div(H2(I(cls="fa-solid fa-user-gear"), " Rendimiento de Mecánicos"),
                Span("Oracle", cls="db-tag oracle"), cls="card-header"),
            Div(tabla_mecanicos, cls="card-body"),
            cls="card mb-2 fade-in"
        ),
        Div(
            Div(H2(I(cls="fa-solid fa-clock-rotate-left"), " Log de Actividad Reciente"),
                Span("MongoDB", cls="db-tag mongo"), cls="card-header"),
            Div(tabla_log, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Reportes", "Reportes del Sistema", "Datos combinados Oracle + MongoDB", contenido)

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

    filas_rep = [
        Tr(Td(d["nombre_pieza"]), Td(str(d["cantidad"])),
           Td(f"S/. {d['precio_unitario']:.2f}"), Td(f"S/. {d['subtotal']:.2f}"))
        for d in detalles
    ]

    seccion_oracle = Div(
        Div(
            H2(I(cls="fa-solid fa-database"), " Datos de la Orden de Trabajo"),
            Span("Oracle (Relacional)", cls="db-tag oracle"),
            style="display:flex;align-items:center;gap:.75rem;margin-bottom:1rem;"
        ),
        Div(
            Div(Label("N° Orden"),    Div(f"#{id_orden}", cls="detail-value font-mono"), cls="detail-item"),
            Div(Label("Cliente"),     Div(cliente.get("nombre","—"), cls="detail-value"), cls="detail-item"),
            Div(Label("DNI"),         Div(cliente.get("dni","—"), cls="detail-value"), cls="detail-item"),
            Div(Label("Vehículo"),    Div(f"{vehiculo.get('marca','')} {vehiculo.get('modelo','')} {vehiculo.get('año','')}", cls="detail-value"), cls="detail-item"),
            Div(Label("Placa"),       Div(Span(vehiculo.get("placa","—"), cls="badge badge-gray font-mono"), cls="detail-value"), cls="detail-item"),
            Div(Label("Mecánico"),    Div(empleado.get("nombre","—"), cls="detail-value"), cls="detail-item"),
            Div(Label("Ingreso"),     Div(orden.get("fecha_ingreso","—"), cls="detail-value"), cls="detail-item"),
            Div(Label("Entrega"),     Div(orden.get("fecha_entrega","—"), cls="detail-value"), cls="detail-item"),
            Div(Label("Estado"),      Div(badge_estado(orden.get("estado","pendiente")), cls="detail-value"), cls="detail-item"),
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
        Div(
            Div(
                Div(Label("N° Factura"),      Div(f"F-{factura['id_factura']:04d}" if factura else "Sin factura", cls="detail-value"), cls="detail-item"),
                Div(Label("Total Facturado"), Div(f"S/. {factura['total']:.2f}" if factura else "—", cls="detail-value", style="color:var(--accent);font-weight:700;"), cls="detail-item"),
                Div(Label("Método de Pago"),  Div(badge_pago(factura["metodo_pago"]) if factura else "—", cls="detail-value"), cls="detail-item"),
                Div(Label("Estado de Pago"),  Div(badge_estado(factura["estado_pago"]) if factura else "—", cls="detail-value"), cls="detail-item"),
                cls="detail-grid"
            ),
            style="margin-top:1.25rem;padding-top:1.25rem;border-top:1px solid var(--border);"
        ),
        cls="card-body"
    )

    if bitacora:
        sintomas = bitacora.get("sintomas", [])
        codigos  = bitacora.get("codigo_OBD", [])
        seccion_mongo_bit = Div(
            Div(H2(I(cls="fa-solid fa-book-open"), " Bitácora de Diagnóstico"), Span("MongoDB", cls="db-tag mongo"), style="display:flex;align-items:center;gap:.75rem;margin-bottom:1rem;"),
            Div(
                Div(Label("Cod Diagnóstico"),    Div(bitacora.get("codigoDiagnostico","—"), cls="detail-value font-mono"), cls="detail-item"),
                Div(Label("Emp ID"),             Div(str(bitacora.get("idEmpleado","—")), cls="detail-value"), cls="detail-item"),
                Div(Label("Cod Especificación"), Div(bitacora.get("codigoEspecificacion","—"), cls="detail-value font-mono"), cls="detail-item"),
                cls="detail-grid"
            ),
            Div(style="margin-top:1rem;"),
            Div(Span(I(cls="fa-solid fa-stethoscope"), " Síntomas", style="font-size:.72rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;"),
                Div(*[Span(s, cls="tag") for s in sintomas], cls="tag-list mt-1") if sintomas else P("—", cls="text-muted text-sm mt-1"),
                style="margin-bottom:1rem;"),
            Div(Span(I(cls="fa-solid fa-triangle-exclamation"), " Códigos OBD", style="font-size:.72rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;"),
                Div(*[Span(c, cls="tag-obd") for c in codigos], cls="tag-list mt-1") if codigos else P("Sin códigos OBD.", cls="text-muted text-sm mt-1"),
                style="margin-bottom:1rem;"),
            Div(Span(I(cls="fa-solid fa-file-lines"), " Observaciones", style="font-size:.72rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;"),
                P(bitacora.get("observaciones","—"), style="margin-top:.4rem;color:var(--text-secondary);font-size:.875rem;line-height:1.6;")),
        )
    else:
        seccion_mongo_bit = Div(
            Div(H2(I(cls="fa-solid fa-book-open"), " Bitácora de Diagnóstico"), Span("MongoDB", cls="db-tag mongo"), style="display:flex;align-items:center;gap:.75rem;margin-bottom:1rem;"),
            Div(I(cls="fa-solid fa-triangle-exclamation"), " Esta orden no tiene bitácora registrada en MongoDB.", cls="alert alert-warning"),
        )

    if esp_tecnica:
        det_tec = esp_tecnica.get("detalles_tecnicos", {})
        seccion_mongo_esp = Div(
            Div(H2(I(cls="fa-solid fa-gear"), " Especificaciones Técnicas"), Span("MongoDB", cls="db-tag mongo"), style="display:flex;align-items:center;gap:.75rem;margin-bottom:1rem;"),
            Div(
                Div(Label("Cod Especificación"), Div(esp_tecnica.get("codigoEspecificacion","—"), cls="detail-value font-mono"), cls="detail-item"),
                Div(Label("Marca / Modelo"),     Div(f"{esp_tecnica.get('marca','?')} / {esp_tecnica.get('modelo','?')}", cls="detail-value"), cls="detail-item"),
                Div(Label("Motor"),              Div(det_tec.get("motor","—"), cls="detail-value"), cls="detail-item"),
                Div(Label("Aceite"),             Div(det_tec.get("aceite","—"), cls="detail-value"), cls="detail-item"),
                Div(Label("Transmisión"),        Div(det_tec.get("transmision","—"), cls="detail-value"), cls="detail-item"),
                Div(Label("Batería / Bujías"),   Div(f"{det_tec.get('batería','?')} {det_tec.get('bujias','')}", cls="detail-value"), cls="detail-item"),
                cls="detail-grid"
            )
        )
    else:
        seccion_mongo_esp = Div(P(I(cls="fa-solid fa-circle-info"), " No se encontraron especificaciones técnicas en MongoDB.", cls="text-muted text-sm"))

    resumen = Div(
        Div(
            Div(H2(I(cls="fa-solid fa-sack-dollar"), " Resumen de Costos"), Span("Oracle + MongoDB", cls="badge badge-orange"), cls="card-header"),
            Div(
                Div(
                    Div(Label("Repuestos (Oracle)"),    Div(f"S/. {total_rep:.2f}", cls="detail-value"), cls="detail-item"),
                    Div(Label("Mano de obra (MongoDB)"), Div(f"S/. {mano_obra:.2f}", cls="detail-value"), cls="detail-item"),
                    Div(Label("GRAN TOTAL"),             Div(f"S/. {gran_total:.2f}", cls="detail-value", style="font-size:1.3rem;font-weight:700;color:var(--accent);"), cls="detail-item"),
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
                H2(I(cls="fa-solid fa-chart-bar"), f" Reporte Integrado — Orden #{id_orden}"),
                Div(Span("Oracle + MongoDB", cls="badge badge-orange"),
                    A(I(cls="fa-solid fa-arrow-left"), " Volver", href="/reportes", cls="btn btn-secondary btn-sm"),
                    cls="flex gap-1", style="align-items:center;"),
                cls="card-header"
            ),
            Div(P(I(cls="fa-solid fa-circle-info"), " Este reporte combina datos relacionales de Oracle con documentos de MongoDB, usando ",
                  Strong("id_vehiculo"), " como campo puente entre ambas bases de datos.", cls="text-muted text-sm"), cls="card-body"),
            cls="card mb-2"
        ),
        Div(Div(Div(H2(I(cls="fa-solid fa-circle", style="color:#f00;font-size:.6rem;vertical-align:middle;"), " Fuente: Oracle Database"), cls="card-header"), seccion_oracle, cls="card fade-in mb-2")),
        Div(Div(Div(H2(I(cls="fa-solid fa-circle", style="color:#0a0;font-size:.6rem;vertical-align:middle;"), " Fuente: MongoDB"), cls="card-header"), Div(seccion_mongo_bit, Div(style="border-top:1px solid var(--border);margin:1.25rem 0;"), seccion_mongo_esp, cls="card-body"), cls="card fade-in mb-2")),
        resumen,
        cls="page-body"
    )
    return layout(req, f"Reporte Orden #{id_orden}", f"Reporte Integrado — Orden #{id_orden}", "Oracle + MongoDB", contenido)