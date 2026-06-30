"""
routes/ordenes.py — View puro de Órdenes de Trabajo
====================================================
Solo renderiza HTML. Lógica en controllers/ordenes_ctrl.py.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout, badge_estado
from datetime import date
import json


def render_ordenes_list(req, usuario, ordenes, todas_ordenes=None, page=1, total_pages=1, total_count=0):
    """Renderiza la lista de órdenes de trabajo."""
    todas_ordenes = todas_ordenes if todas_ordenes is not None else ordenes
    msg = req.query_params.get("msg", "")
    alerts = {
        "creado": Div(
            Div(I(cls="fa-solid fa-circle-check"), " Orden creada correctamente.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        ),
        "actualizado": Div(
            Div(I(cls="fa-solid fa-circle-check"), " Orden actualizada correctamente.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        ),
        "detalle_agregado": Div(
            Div(I(cls="fa-solid fa-circle-check"), " Repuesto agregado a la orden.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        ),
    }
    alert = alerts.get(msg, "")

    # Conteos — sobre el TOTAL de órdenes, no solo la página actual
    pendientes  = sum(1 for o in todas_ordenes if o.get("estado") == "pendiente")
    en_proceso  = sum(1 for o in todas_ordenes if o.get("estado") == "en_proceso")
    completadas = sum(1 for o in todas_ordenes if o.get("estado") == "completada")
    canceladas  = sum(1 for o in todas_ordenes if o.get("estado") == "cancelada")
    total       = len(todas_ordenes)

    grafico = Div(
        Div(
            Div(H2(I(cls="fa-solid fa-chart-pie"), " Resumen de Órdenes"), cls="card-header"),
            Div(
                Div(
                    Div(
                        Canvas(id="ordenesChart", style="max-height:200px;max-width:200px;"),
                        Div(
                            Div(str(total), style="font-size:1.8rem;font-weight:800;color:var(--brand-primary);line-height:1;"),
                            Div("órdenes", style="font-size:.72rem;color:var(--text-muted);font-weight:500;"),
                            style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;"
                        ),
                        style="position:relative;display:flex;align-items:center;justify-content:center;"
                    ),
                    Div(
                        Div(
                            Div(
                                Div(style="width:10px;height:10px;border-radius:3px;background:#F59E0B;flex-shrink:0;"),
                                Div(
                                    Div("Pendientes", style="font-size:.73rem;color:var(--text-muted);"),
                                    Div(str(pendientes), style="font-size:1.35rem;font-weight:800;color:var(--text-primary);line-height:1;"),
                                ),
                                style="display:flex;align-items:center;gap:.5rem;"
                            ),
                            Div(
                                Div(style="width:10px;height:10px;border-radius:3px;background:#10B981;flex-shrink:0;"),
                                Div(
                                    Div("Completadas", style="font-size:.73rem;color:var(--text-muted);"),
                                    Div(str(completadas), style="font-size:1.35rem;font-weight:800;color:var(--text-primary);line-height:1;"),
                                ),
                                style="display:flex;align-items:center;gap:.5rem;"
                            ),
                            style="display:flex;flex-direction:column;gap:1rem;"
                        ),
                        Div(
                            Div(
                                Div(style="width:10px;height:10px;border-radius:3px;background:#3B82F6;flex-shrink:0;"),
                                Div(
                                    Div("En Proceso", style="font-size:.73rem;color:var(--text-muted);"),
                                    Div(str(en_proceso), style="font-size:1.35rem;font-weight:800;color:var(--text-primary);line-height:1;"),
                                ),
                                style="display:flex;align-items:center;gap:.5rem;"
                            ),
                            Div(
                                Div(style="width:10px;height:10px;border-radius:3px;background:#EF4444;flex-shrink:0;"),
                                Div(
                                    Div("Canceladas", style="font-size:.73rem;color:var(--text-muted);"),
                                    Div(str(canceladas), style="font-size:1.35rem;font-weight:800;color:var(--text-primary);line-height:1;"),
                                ),
                                style="display:flex;align-items:center;gap:.5rem;"
                            ),
                            style="display:flex;flex-direction:column;gap:1rem;"
                        ),
                        style="display:grid;grid-template-columns:1fr 1fr;gap:1rem 2rem;align-content:center;"
                    ),
                    style="display:flex;align-items:center;justify-content:center;gap:3rem;"
                ),
                cls="card-body", style="padding:1.75rem;"
            ),
            cls="card fade-in"
        ),
        Script(src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"),
        Script(f"""
            document.addEventListener('DOMContentLoaded', function() {{
                const ctx = document.getElementById('ordenesChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['Pendientes', 'En Proceso', 'Completadas', 'Canceladas'],
                        datasets: [{{
                            data: [{pendientes}, {en_proceso}, {completadas}, {canceladas}],
                            backgroundColor: ['#F59E0B', '#3B82F6', '#10B981', '#EF4444'],
                            borderWidth: 3,
                            borderColor: '#ffffff',
                            hoverOffset: 6,
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: true,
                        cutout: '70%',
                        plugins: {{
                            legend: {{ display: false }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(ctx) {{
                                        const pct = {total} > 0 ? Math.round(ctx.parsed / {total} * 100) : 0;
                                        return ` ${{ctx.label}}: ${{ctx.parsed}} (${{pct}}%)`;
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
            }});
        """),
        style="margin-bottom:1.25rem;"
    )

    filas = []
    for o in ordenes:
        fecha_ing = str(o.get("fecha_ingreso", "—")).split(" ")[0]
        fecha_ent = str(o.get("fecha_entrega", "—")).split(" ")[0]

        acciones = [
            A(
                I(cls="fa-solid fa-eye"),
                href=f"/ordenes/{o.get('id_orden', '')}",
                cls="btn-icon icon-view",
                **{"data-tooltip": "Ver detalle"}
            )
        ]
        if puede_acceder(usuario, "ordenes", "editar"):
            acciones.append(
                A(
                    I(cls="fa-solid fa-pen"),
                    href=f"/ordenes/{o.get('id_orden', '')}",
                    cls="btn-icon icon-edit",
                    **{"data-tooltip": "Ver y editar"}
                )
            )

        orden_badge = Div(
            I(cls="fa-solid fa-clipboard-list orden-icon"),
            Span(f"#{o.get('id_orden', '—')}", cls="orden-id-texto"),
            cls="orden-id-badge"
        )

        filas.append(Tr(
            Td(orden_badge, cls="td-orden-id"),
            Td(Span(o.get("placa", "—"), cls="badge badge-gray font-mono")),
            Td(o.get("nombre_cliente", "—")),
            Td(o.get("nombre_empleado", "—")),
            Td(Span(fecha_ing, cls="fecha-cell")),
            Td(Span(fecha_ent, cls="fecha-cell")),
            Td(badge_estado(o.get("estado", "—"))),
            Td(Div(*acciones, cls="row-actions")),
        ))

    tabla = Div(
        Table(
            Thead(Tr(
                Th("#"),
                Th("Placa"),
                Th("Cliente"),
                Th("Mecánico"),
                Th("Ingreso"),
                Th("Entrega"),
                Th("Estado"),
                Th("Acciones")
            )),
            Tbody(*filas) if filas else Tbody(
                Tr(Td("No hay órdenes registradas.", colspan="8", cls="no-data"))
            ),
        ),
        cls="table-wrap"
    )

    crear_btn = A(
        I(cls="fa-solid fa-plus"), " Nueva Orden",
        href="/ordenes/nueva", cls="btn btn-primary"
    ) if puede_acceder(usuario, "ordenes", "crear") else ""

    # ── Paginación (mismo patrón que Repuestos/Cotizaciones) ─────────
    max_visible = 5
    half = max_visible // 2

    start_page = page - half
    end_page = page + half

    if start_page < 1:
        end_page += (1 - start_page)
        start_page = 1

    if end_page > total_pages:
        start_page -= (end_page - total_pages)
        end_page = total_pages
        if start_page < 1:
            start_page = 1

    page_buttons = []
    for p in range(start_page, end_page + 1):
        is_current = (p == page)
        btn_cls = "btn btn-sm btn-primary" if is_current else "btn btn-sm btn-secondary"
        page_buttons.append(
            A(str(p), href=f"/ordenes?page={p}", cls=btn_cls, style="min-width:32px; text-align:center;")
        )

    if page > 1:
        pag_prev = A(I(cls="fa-solid fa-chevron-left"), " Anterior",
                     href=f"/ordenes?page={page - 1}", cls="btn btn-sm btn-secondary")
    else:
        pag_prev = Span(I(cls="fa-solid fa-chevron-left"), " Anterior",
                        cls="btn btn-sm btn-secondary disabled", style="opacity:0.5; cursor:not-allowed;")

    if page < total_pages:
        pag_next = A("Siguiente ", I(cls="fa-solid fa-chevron-right"),
                     href=f"/ordenes?page={page + 1}", cls="btn btn-sm btn-secondary")
    else:
        pag_next = Span("Siguiente ", I(cls="fa-solid fa-chevron-right"),
                        cls="btn btn-sm btn-secondary disabled", style="opacity:0.5; cursor:not-allowed;")

    start_item = (page - 1) * 6 + 1 if total_count > 0 else 0
    end_item = min(page * 6, total_count)

    paginacion = Div(
        Span(f"Mostrando {start_item}–{end_item} de {total_count} registros", cls="text-muted text-sm"),
        Div(pag_prev, *page_buttons, pag_next, cls="paginacion-nav"),
        cls="paginacion-container"
    )

    contenido = Div(
        Style("""
            .orden-id-badge {
                display: inline-flex;
                align-items: center;
                gap: 0;
                background: var(--brand-secondary-light);
                border: 1.5px solid #c8d4db;
                border-radius: 8px;
                padding: .3rem .65rem;
                font-family: monospace;
                font-size: .82rem;
                font-weight: 700;
                color: var(--brand-secondary);
                letter-spacing: .04em;
                overflow: hidden;
                transition: background .2s, border-color .2s, color .2s, box-shadow .2s;
            }
            .orden-icon {
                font-size: .85rem;
                max-width: 0;
                opacity: 0;
                overflow: hidden;
                transition: max-width .25s ease, opacity .2s ease, margin-right .25s ease;
                margin-right: 0;
                color: var(--brand-primary);
            }
            tr:hover .orden-id-badge {
                background: var(--brand-primary-light);
                border-color: rgba(122,12,17,.3);
                color: var(--brand-primary);
                box-shadow: 0 2px 8px rgba(122,12,17,.12);
            }
            tr:hover .orden-icon {
                max-width: 20px;
                opacity: 1;
                margin-right: .4rem;
            }
            .td-orden-id { width: 80px; }
            .fecha-cell {
                font-size: .82rem;
                font-family: monospace;
                color: var(--text-secondary);
            }
        """),
        alert,
        grafico,
        Div(
            Div(H2(I(cls="fa-solid fa-clipboard-list"), " Órdenes de Trabajo"), cls="card-header"),
            Div(
                Div(
                    Span(f"{total} órdenes", cls="text-muted text-sm"),
                    crear_btn,
                    cls="flex gap-2",
                    style="justify-content:space-between;align-items:center;margin-bottom:1rem;"
                ),
                tabla,
                paginacion,
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Órdenes", "Órdenes de Trabajo", "Seguimiento de reparaciones activas", contenido)


def render_ordenes_detalle(req, usuario, orden, repuestos, cotizacion_vehiculo=None):
    """
    Vista detalle completa — info + estado + repuestos (con quitar) + agregar + tabla final.

    cotizacion_vehiculo: la única cotización vigente del vehículo de esta orden (o None).
    Se usa tanto para mostrar el botón "Cargar Cotización" (si aún no se cargó nada)
    como para construir la TABLA FINAL (repuestos reales + servicios), que es la que
    se imprime en el PDF.
    """
    id_orden = orden["id_orden"]
    msg  = req.query_params.get("msg", "")
    advertencia = req.query_params.get("advertencia", "")

    alert = ""
    if msg == "detalle_agregado":
        alert = Div(
            Div(I(cls="fa-solid fa-circle-check"), " Repuesto agregado correctamente.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        )
    elif msg == "cotizacion_cargada":
        alert = Div(
            Div(I(cls="fa-solid fa-circle-check"), " Cotización cargada correctamente en la orden.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        )
    elif msg == "repuesto_quitado":
        alert = Div(
            Div(I(cls="fa-solid fa-circle-check"), " Repuesto eliminado y stock repuesto.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        )

    alert_advertencia = ""
    if advertencia:
        alert_advertencia = Div(
            Div(I(cls="fa-solid fa-triangle-exclamation"), f" {advertencia}", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-warning alert-dismissible"
        )

    v        = orden.get("vehiculo") or {}
    e        = orden.get("empleado") or {}
    c        = orden.get("cliente")  or {}
    detalles = orden.get("detalles", [])
    total_repuestos = sum(d["subtotal"] for d in detalles)

    fecha_ing = str(orden.get("fecha_ingreso", "—")).split(" ")[0]
    fecha_ent = str(orden.get("fecha_entrega", "—")).split(" ")[0]

    # ── Cambiar estado inline ────────────────────────────────────────
    cambiar_estado = ""
    if puede_acceder(usuario, "ordenes", "editar"):
        estados_opts = [
            Option("Pendiente",  value="pendiente",  selected=(orden["estado"] == "pendiente")),
            Option("En Proceso", value="en_proceso", selected=(orden["estado"] == "en_proceso")),
            Option("Completada", value="completada", selected=(orden["estado"] == "completada")),
            Option("Cancelada",  value="cancelada",  selected=(orden["estado"] == "cancelada")),
        ]
        cambiar_estado = Form(
            Input(type="hidden", name="id_orden", value=str(id_orden)),
            Div(
                Select(*estados_opts, name="estado", style="width:auto;min-width:140px;"),
                Button(I(cls="fa-solid fa-rotate"), " Actualizar estado",
                       type="submit", cls="btn btn-primary btn-sm"),
                cls="flex gap-1", style="align-items:center;"
            ),
            method="post", action="/ordenes/cambiar-estado"
        )

    # ── Filas de repuestos (con botón Quitar) ─────────────────────────
    puede_editar = puede_acceder(usuario, "ordenes", "editar")
    filas_det = []
    for d in detalles:
        quitar_btn = ""
        if puede_editar:
            quitar_btn = Form(
                Input(type="hidden", name="id_orden", value=str(id_orden)),
                Input(type="hidden", name="id_detalle", value=str(d["id_detalle"])),
                Button(
                    I(cls="fa-solid fa-trash"),
                    type="submit", cls="btn-icon icon-delete",
                    onclick="return confirm('¿Quitar este repuesto? Se repondrá al stock.');",
                    **{"data-tooltip": "Quitar repuesto"}
                ),
                method="post", action="/ordenes/quitar-repuesto",
                style="display:inline;"
            )
        filas_det.append(Tr(
            Td(d["nombre_pieza"], style="font-weight:500;"),
            Td(str(d["cantidad"]), style="text-align:center;"),
            Td(f"S/. {d['precio_unitario']:.2f}"),
            Td(f"S/. {d['subtotal']:.2f}",
               style="font-weight:700;color:var(--brand-primary);text-align:right;"),
            Td(quitar_btn, style="text-align:center;"),
        ))

    # ── Formulario agregar repuesto (precio autocompletado, solo lectura) ──
    agregar_form = ""
    if puede_acceder(usuario, "ordenes", "crear"):
        opts = [
            Option(
                f"{r['nombre']} (Stock: {r['stock']})",
                value=str(r["id_pieza"]),
                **{"data-precio": f"{r['precio_venta']:.2f}", "data-stock": str(r["stock"])}
            )
            for r in repuestos
        ]
        agregar_form = Div(
            Div(
                I(cls="fa-solid fa-circle-plus",
                  style="color:var(--brand-secondary);"),
                " Agregar Repuesto",
                style="font-size:.85rem;font-weight:700;color:var(--text-primary);"
                      "text-transform:uppercase;letter-spacing:.05em;margin-bottom:.75rem;"
                      "display:flex;align-items:center;gap:.4rem;"
            ),
            Form(
                Input(type="hidden", name="id_orden", value=str(id_orden)),
                Div(
                    Div(Label("Repuesto"),
                        Select(*opts, name="id_pieza", id="select-repuesto-agregar",
                               onchange="autocompletarPrecioRepuesto()", required=True),
                        cls="form-group"),
                    Div(Label("Cantidad"),
                        Input(name="cantidad", type="number", min="1", value="1", required=True),
                        cls="form-group"),
                    Div(Label("Precio unitario (S/.)"),
                        Input(id="input-precio-agregar", name="precio_unitario", type="number",
                              step="0.01", min="0", readonly=True,
                              style="background:var(--brand-secondary-light);color:var(--text-muted);"),
                        cls="form-group"),
                    cls="form-grid"
                ),
                Div(
                    Button(I(cls="fa-solid fa-plus"), " Agregar Repuesto",
                           type="submit", cls="btn btn-primary"),
                    cls="form-actions"
                ),
                method="post", action="/ordenes/agregar-repuesto"
            ),
            Script("""
                function autocompletarPrecioRepuesto() {
                    const sel = document.getElementById('select-repuesto-agregar');
                    const precio = document.getElementById('input-precio-agregar');
                    const opt = sel.options[sel.selectedIndex];
                    precio.value = opt && opt.dataset.precio ? opt.dataset.precio : '';
                }
                document.addEventListener('DOMContentLoaded', autocompletarPrecioRepuesto);
            """),
            style="margin-top:1.5rem;padding-top:1.5rem;border-top:1px solid var(--border);"
        )

    # ── Clasificar la cotización vigente (servicios vs repuestos) ────
    # Esto alimenta tanto el botón "Cargar Cotización" como la TABLA FINAL.
    clasificacion = None
    if cotizacion_vehiculo:
        from controllers import deps
        clasificacion = deps.ordenes.clasificar_cotizacion(cotizacion_vehiculo, repuestos)

    # ── Cargar Cotización (solo si aún no hay repuestos en la orden) ──
    cargar_cotizacion_seccion = ""
    if puede_acceder(usuario, "ordenes", "crear") and cotizacion_vehiculo and not detalles:
        codigo_cot = cotizacion_vehiculo.get("codigoCotizacion", "")
        fecha_val = str(cotizacion_vehiculo.get("fecha_validez_str") or cotizacion_vehiculo.get("fecha_validez", ""))[:10]

        cargar_cotizacion_seccion = Div(
            Div(
                I(cls="fa-solid fa-file-invoice-dollar", style="color:var(--brand-secondary);"),
                " Cargar Cotización al Trabajo",
                style="font-size:.85rem;font-weight:700;color:var(--text-primary);"
                    "text-transform:uppercase;letter-spacing:.05em;margin-bottom:.75rem;"
                    "display:flex;align-items:center;gap:.4rem;"
            ),
            P(
                f"Cotización vigente para este vehículo: ",
                Span(codigo_cot, style="font-family:monospace;font-weight:700;color:var(--brand-primary);"),
                f" — válida hasta {fecha_val}. Al cargar, los repuestos cotizados se insertan como "
                "filas reales en esta orden (descontando inventario). Los servicios cotizados se "
                "muestran como parte del total impreso, sin afectar el inventario.",
                style="font-size:.8rem;color:var(--text-muted);margin-bottom:.75rem;"
            ),
            Form(
                Input(type="hidden", name="id_orden", value=str(id_orden)),
                Input(type="hidden", name="codigo_cotizacion", value=codigo_cot),
                Button(I(cls="fa-solid fa-download"), " Cargar Cotización",
                       type="submit", cls="btn btn-secondary btn-sm",
                       onclick="return confirm('¿Cargar esta cotización? Esto insertará los repuestos cotizados en la orden y descontará inventario.');"),
                method="post", action="/ordenes/cargar-cotizacion"
            ),
            style="margin-top:1.5rem;padding-top:1.5rem;border-top:1px solid var(--border);"
        )

    # ── TABLA FINAL (repuestos reales de Oracle + servicios de la cotización) ──
    # Esta es la tabla que define lo que se imprime en el PDF.
    servicios_cotizacion = clasificacion["servicios"] if clasificacion else []
    total_servicios = sum(s["precio"] for s in servicios_cotizacion)
    total_general = total_repuestos + total_servicios

    filas_finales = []
    for d in detalles:
        filas_finales.append(Tr(
            Td(d["nombre_pieza"]),
            Td(Span("Repuesto", cls="badge badge-gray", style="font-size:.7rem;")),
            Td(str(d["cantidad"]), style="text-align:center;"),
            Td(f"S/. {d['subtotal']:.2f}", style="text-align:right;font-weight:600;"),
        ))
    for s in servicios_cotizacion:
        filas_finales.append(Tr(
            Td(s["item"]),
            Td(Span("Servicio", style="font-size:.7rem;background:#FEF3C7;color:#92400E;"
                                       "padding:.15rem .5rem;border-radius:6px;")),
            Td("—", style="text-align:center;color:var(--text-muted);"),
            Td(f"S/. {s['precio']:.2f}", style="text-align:right;font-weight:600;"),
        ))

    tabla_final_seccion = Div(
        Div(
            I(cls="fa-solid fa-receipt", style="color:var(--brand-secondary);"),
            " Tabla Total de la Orden (para impresión)",
            style="font-size:.85rem;font-weight:700;color:var(--text-primary);"
                  "text-transform:uppercase;letter-spacing:.05em;margin-bottom:.75rem;"
                  "display:flex;align-items:center;gap:.4rem;"
        ),
        Div(
            Table(
                Thead(Tr(
                    Th("Ítem"), Th("Tipo"), Th("Cantidad", style="text-align:center;"),
                    Th("Importe", style="text-align:right;")
                )),
                Tbody(*filas_finales) if filas_finales else Tbody(
                    Tr(Td("Sin ítems registrados aún.", colspan="4", cls="no-data"))
                ),
            ),
            cls="table-wrap"
        ),
        Div(
            Span("Total General:", style="color:var(--text-muted);font-size:.85rem;"),
            Span(f"S/. {total_general:.2f}",
                 style="font-size:1.4rem;font-weight:800;color:var(--brand-primary);"),
            cls="flex gap-2", style="justify-content:flex-end;align-items:center;margin-top:.75rem;"
        ),
        style="margin-top:1.5rem;padding-top:1.5rem;border-top:2px solid var(--brand-primary);"
    )

    # ── Botón Imprimir (solo si está completada) ─────────────────────
    imprimir_btn = ""
    if orden.get("estado") == "completada":
        imprimir_btn = A(
            I(cls="fa-solid fa-file-pdf"), " Imprimir Orden (PDF)",
            href=f"/ordenes/{id_orden}/imprimir",
            cls="btn btn-primary",
            target="_blank"
        )

    contenido = Div(
        alert,
        alert_advertencia,
        Div(
            Div(
                Div(
                    H2(I(cls="fa-solid fa-clipboard-list"), f" Orden #{id_orden}"),
                    badge_estado(orden["estado"]),
                    cls="flex gap-2", style="align-items:center;"
                ),
                Div(
                    imprimir_btn,
                    A(I(cls="fa-solid fa-arrow-left"), " Volver",
                      href="/ordenes", cls="btn btn-secondary btn-sm"),
                    cls="flex gap-2"
                ),
                cls="card-header"
            ),
            Div(
                Div(
                    Div(
                        Div(
                            I(cls="fa-solid fa-user", style="color:var(--brand-secondary);font-size:.8rem;"),
                            " CLIENTE",
                            style="font-size:.7rem;font-weight:700;color:var(--text-muted);"
                                  "text-transform:uppercase;letter-spacing:.06em;"
                                  "display:flex;align-items:center;gap:.3rem;margin-bottom:.3rem;"
                        ),
                        Div(c.get("nombre", "—"), style="font-weight:600;font-size:.95rem;"),
                        cls="detail-item"
                    ),
                    Div(
                        Div(
                            I(cls="fa-solid fa-car", style="color:var(--brand-secondary);font-size:.8rem;"),
                            " VEHÍCULO",
                            style="font-size:.7rem;font-weight:700;color:var(--text-muted);"
                                  "text-transform:uppercase;letter-spacing:.06em;"
                                  "display:flex;align-items:center;gap:.3rem;margin-bottom:.3rem;"
                        ),
                        Div(
                            Span(v.get("placa",""), cls="badge badge-gray font-mono",
                                 style="margin-right:.4rem;"),
                            f"{v.get('marca','')} {v.get('modelo','')}",
                            style="font-weight:600;font-size:.95rem;display:flex;align-items:center;"
                        ),
                        cls="detail-item"
                    ),
                    Div(
                        Div(
                            I(cls="fa-solid fa-wrench", style="color:var(--brand-secondary);font-size:.8rem;"),
                            " MECÁNICO",
                            style="font-size:.7rem;font-weight:700;color:var(--text-muted);"
                                  "text-transform:uppercase;letter-spacing:.06em;"
                                  "display:flex;align-items:center;gap:.3rem;margin-bottom:.3rem;"
                        ),
                        Div(e.get("nombre", "—"), style="font-weight:600;font-size:.95rem;"),
                        cls="detail-item"
                    ),
                    Div(
                        Div(
                            I(cls="fa-solid fa-calendar", style="color:var(--brand-secondary);font-size:.8rem;"),
                            " INGRESO",
                            style="font-size:.7rem;font-weight:700;color:var(--text-muted);"
                                  "text-transform:uppercase;letter-spacing:.06em;"
                                  "display:flex;align-items:center;gap:.3rem;margin-bottom:.3rem;"
                        ),
                        Div(fecha_ing, style="font-weight:600;font-size:.95rem;font-family:monospace;"),
                        cls="detail-item"
                    ),
                    Div(
                        Div(
                            I(cls="fa-solid fa-calendar-check", style="color:var(--brand-secondary);font-size:.8rem;"),
                            " ENTREGA ESTIMADA",
                            style="font-size:.7rem;font-weight:700;color:var(--text-muted);"
                                  "text-transform:uppercase;letter-spacing:.06em;"
                                  "display:flex;align-items:center;gap:.3rem;margin-bottom:.3rem;"
                        ),
                        Div(fecha_ent, style="font-weight:600;font-size:.95rem;font-family:monospace;"),
                        cls="detail-item"
                    ),
                    Div(
                        Div(
                            I(cls="fa-solid fa-rotate", style="color:var(--brand-secondary);font-size:.8rem;"),
                            " ESTADO",
                            style="font-size:.7rem;font-weight:700;color:var(--text-muted);"
                                  "text-transform:uppercase;letter-spacing:.06em;"
                                  "display:flex;align-items:center;gap:.3rem;margin-bottom:.3rem;"
                        ),
                        Div(cambiar_estado if cambiar_estado else badge_estado(orden["estado"])),
                        cls="detail-item"
                    ),
                    cls="detail-grid"
                ),

                Div(style="margin-top:1.5rem;padding-top:1.5rem;border-top:1px solid var(--border);"),

                Div(
                    I(cls="fa-solid fa-screwdriver-wrench",
                      style="color:var(--brand-secondary);"),
                    " Repuestos Utilizados",
                    style="font-size:.85rem;font-weight:700;color:var(--text-primary);"
                          "text-transform:uppercase;letter-spacing:.05em;margin-bottom:.75rem;"
                          "display:flex;align-items:center;gap:.4rem;"
                ),
                Div(
                    Table(
                        Thead(Tr(
                            Th("Repuesto"),
                            Th("Cantidad", style="text-align:center;"),
                            Th("Precio Unit."),
                            Th("Subtotal", style="text-align:right;"),
                            Th("")
                        )),
                        Tbody(*filas_det) if filas_det else Tbody(
                            Tr(Td("Sin repuestos agregados.", colspan="5", cls="no-data"))
                        ),
                    ),
                    cls="table-wrap"
                ),
                Div(
                    Span("Total Repuestos:", style="color:var(--text-muted);font-size:.85rem;"),
                    Span(f"S/. {total_repuestos:.2f}",
                         style="font-size:1.3rem;font-weight:800;color:var(--brand-primary);"),
                    cls="flex gap-2", style="justify-content:flex-end;align-items:center;margin-top:.75rem;"
                ),

                agregar_form,
                cargar_cotizacion_seccion,
                tabla_final_seccion,

                cls="card-body"
            ),
            cls="card fade-in"
        ),

        cls="page-body"
    )
    return layout(req, f"Orden #{id_orden}", f"Orden de Trabajo #{id_orden}",
                  c.get("nombre", ""), contenido)


def render_ordenes_nueva(req, vehiculos, mecanicos, cotizaciones_por_vehiculo=None):
    """Formulario de nueva orden — con modal informativo 'Ver Cotizaciones'."""
    cotizaciones_por_vehiculo = cotizaciones_por_vehiculo or {}
    hoy    = date.today().strftime("%Y-%m-%d")
    opts_v = [
        Option(
            f"{v['placa']} — {v['marca']} {v['modelo']}",
            value=str(v["id_vehiculo"]),
            **{"data-tiene-cotizacion": "1" if v["id_vehiculo"] in cotizaciones_por_vehiculo else "0"}
        )
        for v in vehiculos
    ]
    opts_e = [Option(f"{e['nombre']} · {e.get('especialidad','—')}",
                     value=str(e["id_empleado"])) for e in mecanicos]

    ver_cotizaciones_btn = Button(
        I(cls="fa-solid fa-file-invoice-dollar"), " Ver Cotizaciones",
        type="button", id="btn-ver-cotizaciones", cls="btn btn-secondary btn-sm",
        style="display:none;width:fit-content;", onclick="abrirModalCotizaciones()"
    )

    form = Form(
        Div(
            Div(Label("Vehículo"),
                Select(Option("-- Seleccionar vehículo --", value=""),
                    *opts_v, name="id_vehiculo", id="select-vehiculo", required=True),
                ver_cotizaciones_btn,
                cls="form-group",
                style="display:flex;flex-direction:column;gap:.5rem;align-items:flex-start;"),
            Div(Label("Mecánico asignado"),
                Select(Option("-- Seleccionar mecánico --", value=""),
                    *opts_e, name="id_empleado", required=True),
                cls="form-group"),
            Div(Label("Fecha de ingreso"),
                Input(name="fecha_ingreso", type="date", value=hoy, min=hoy, required=True),
                cls="form-group"),
            Div(Label("Fecha estimada de entrega"),
                Input(name="fecha_entrega", type="date", min=hoy, required=True),
                cls="form-group"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/ordenes", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Crear Orden",
                type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/ordenes/crear"
    )

    modal_cotizaciones = Div(
        Div(
            Div(
                H3(I(cls="fa-solid fa-file-invoice-dollar"), " Cotizaciones Vigentes del Vehículo"),
                Button("×", onclick="cerrarModalCotizaciones()", cls="tech-modal-close", type="button"),
                cls="tech-modal-header"
            ),
            Div(
                id="cotizaciones-modal-body",
                cls="tech-modal-body"
            ),
            cls="tech-modal-content"
        ),
        id="cotizaciones-modal",
        cls="tech-modal"
    )

    cotizaciones_dict = {
        str(id_veh): [
            {
                "codigo": cot.get("codigoCotizacion", "—"),
                "total": cot.get("total", 0.0),
                "fecha_validez": str(cot.get("fecha_validez_str") or cot.get("fecha_validez", ""))[:10],
                "items": cot.get("servicios_repuestos", []),
                "es_vigente_real": (idx == 0),  # la primera de la lista ordenada = la actual
            }
            for idx, cot in enumerate(lista)
        ]
        for id_veh, lista in cotizaciones_por_vehiculo.items()
    }

    js_cotizaciones = Script(f"""
        const cotizacionesPorVehiculo = {json.dumps(cotizaciones_dict)};

        function actualizarBotonCotizaciones() {{
            const sel = document.getElementById('select-vehiculo');
            const btn = document.getElementById('btn-ver-cotizaciones');
            const tieneCot = sel.value && cotizacionesPorVehiculo[sel.value] &&
                              cotizacionesPorVehiculo[sel.value].length > 0;
            btn.style.display = tieneCot ? 'inline-flex' : 'none';
        }}

        function abrirModalCotizaciones() {{
            const sel = document.getElementById('select-vehiculo');
            const lista = cotizacionesPorVehiculo[sel.value] || [];
            const body = document.getElementById('cotizaciones-modal-body');

            if (lista.length === 0) {{
                body.innerHTML = '<p style="text-align:center;padding:1.5rem;color:var(--text-muted);">Sin cotizaciones vigentes.</p>';
            }} else {{
                let html = '';
                lista.forEach(function(cot) {{
                    const apagada = !cot.es_vigente_real;
                    const estiloCard = apagada
                        ? 'border:1px solid var(--border);border-radius:10px;padding:1rem;margin-bottom:.85rem;position:relative;opacity:.5;filter:grayscale(40%);'
                        : 'border:2px solid var(--brand-primary);border-radius:10px;padding:1rem;margin-bottom:.85rem;position:relative;';

                    html += '<div style="' + estiloCard + '">';

                    if (apagada) {{
                        html += '<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%) rotate(-18deg);' +
                                'font-size:1.4rem;font-weight:900;color:rgba(122,12,17,.35);letter-spacing:.1em;' +
                                'text-transform:uppercase;pointer-events:none;z-index:2;border:3px solid rgba(122,12,17,.35);' +
                                'padding:.2rem .8rem;border-radius:8px;">NO VIGENTE</div>';
                    }}

                    html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.5rem;">';
                    html += '<span style="font-weight:700;font-family:monospace;color:var(--brand-primary);">' + cot.codigo + '</span>';
                    if (!apagada) {{
                        html += '<span style="font-size:.7rem;background:#DCFCE7;color:#166534;padding:.15rem .5rem;border-radius:6px;font-weight:700;">ACTUAL</span>';
                    }}
                    html += '<span style="font-size:.78rem;color:var(--text-muted);">Válida hasta ' + cot.fecha_validez + '</span>';
                    html += '</div>';
                    html += '<table style="width:100%;font-size:.85rem;">';
                    cot.items.forEach(function(it) {{
                        html += '<tr><td style="padding:.25rem 0;">' + it.item + '</td>' +
                                '<td style="text-align:right;padding:.25rem 0;">S/. ' + Number(it.precio).toFixed(2) + '</td></tr>';
                    }});
                    html += '</table>';
                    html += '<div style="text-align:right;margin-top:.5rem;font-weight:800;color:var(--brand-primary);">Total: S/. ' + Number(cot.total).toFixed(2) + '</div>';
                    html += '</div>';
                }});
                body.innerHTML = html;
            }}

            document.getElementById('cotizaciones-modal').classList.add('active');
        }}

        function cerrarModalCotizaciones() {{
            document.getElementById('cotizaciones-modal').classList.remove('active');
        }}

        window.addEventListener('click', function(e) {{
            const modal = document.getElementById('cotizaciones-modal');
            if (e.target === modal) cerrarModalCotizaciones();
        }});

        document.addEventListener('DOMContentLoaded', function() {{
            const sel = document.getElementById('select-vehiculo');
            sel.addEventListener('change', actualizarBotonCotizaciones);
        }});
    """)

    contenido = Div(
        Div(
            Div(
                H2(I(cls="fa-solid fa-clipboard-list"), " Nueva Orden de Trabajo"),
                A(I(cls="fa-solid fa-arrow-left"), " Volver",
                  href="/ordenes", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(form, cls="card-body"),
            cls="form-card fade-in"
        ),
        modal_cotizaciones,
        js_cotizaciones,
        cls="page-body"
    )
    return layout(req, "Nueva Orden", "Nueva Orden de Trabajo",
                  "Generación de Orden de Trabajo", contenido)


def render_ordenes_editar(req, orden, vehiculos, empleados):
    """Formulario de edición — datos de la orden únicamente."""
    id_orden = orden["id_orden"]
    opts_v = [
        Option(f"{v['placa']} — {v['marca']} {v['modelo']}",
               value=str(v["id_vehiculo"]),
               selected=(v["id_vehiculo"] == orden["id_vehiculo"]))
        for v in vehiculos
    ]
    opts_e = [
        Option(f"{e['nombre']}", value=str(e["id_empleado"]),
               selected=(e["id_empleado"] == orden["id_empleado"]))
        for e in empleados
    ]
    estados_opts = [
        Option("Pendiente",  value="pendiente",  selected=(orden["estado"] == "pendiente")),
        Option("En Proceso", value="en_proceso", selected=(orden["estado"] == "en_proceso")),
        Option("Completada", value="completada", selected=(orden["estado"] == "completada")),
        Option("Cancelada",  value="cancelada",  selected=(orden["estado"] == "cancelada")),
    ]

    fecha_ing = str(orden.get("fecha_ingreso", "")).split(" ")[0]
    fecha_ent = str(orden.get("fecha_entrega", "")).split(" ")[0]

    form = Form(
        Div(
            Div(Label("Vehículo"),
                Select(*opts_v, name="id_vehiculo", required=True),
                cls="form-group"),
            Div(Label("Mecánico"),
                Select(*opts_e, name="id_empleado", required=True),
                cls="form-group"),
            Div(Label("Fecha ingreso"),
                Input(name="fecha_ingreso", type="date", value=fecha_ing, required=True),
                cls="form-group"),
            Div(Label("Fecha entrega"),
                Input(name="fecha_entrega", type="date", value=fecha_ent, required=True),
                cls="form-group"),
            Div(Label("Estado"),
                Select(*estados_opts, name="estado", required=True),
                cls="form-group"),
            cls="form-grid"
        ),
        Input(type="hidden", name="id_orden", value=str(id_orden)),
        Div(
            A("Cancelar", href=f"/ordenes/{id_orden}", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Guardar cambios",
                   type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/ordenes/actualizar"
    )

    contenido = Div(
        Div(
            Div(
                H2(I(cls="fa-solid fa-pen"), f" Editar Orden #{id_orden}"),
                A(I(cls="fa-solid fa-arrow-left"), " Volver al detalle",
                  href=f"/ordenes/{id_orden}", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(form, cls="card-body"),
            cls="form-card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Editar Orden", f"Editar Orden #{id_orden}", "", contenido)


def render_orden_pdf_html(orden: dict, servicios_cotizacion: list = None) -> str:
    """
    Genera el HTML del comprobante de Orden de Trabajo completada,
    estilo factura comercial, para convertir a PDF con xhtml2pdf.

    Incluye TODOS los repuestos reales (DETALLE_ORDEN_REPUESTOS) +
    los servicios de la cotización vigente del vehículo (informativos).
    Calcula Subtotal, IGV (18%) y Total.
    """
    servicios_cotizacion = servicios_cotizacion or []
    id_orden = orden["id_orden"]
    v = orden.get("vehiculo") or {}
    e = orden.get("empleado") or {}
    c = orden.get("cliente") or {}
    detalles = orden.get("detalles", [])

    subtotal = sum(d["subtotal"] for d in detalles) + sum(s["precio"] for s in servicios_cotizacion)
    igv = subtotal * 0.18
    total = subtotal + igv

    fecha_ing = str(orden.get("fecha_ingreso", "—")).split(" ")[0]
    fecha_ent = str(orden.get("fecha_entrega", "—")).split(" ")[0]

    item_num = 1
    filas_html = ""
    for d in detalles:
        filas_html += f"""
            <tr>
                <td style="text-align:center;">{item_num}</td>
                <td style="text-align:center;">{d['cantidad']}</td>
                <td>{d.get('codigo_pieza', '—')}</td>
                <td>{d['nombre_pieza']}</td>
                <td style="text-align:center;">Repuesto</td>
                <td style="text-align:right;">S/. {d['precio_unitario']:.2f}</td>
                <td style="text-align:right;">S/. {d['subtotal']:.2f}</td>
            </tr>
        """
        item_num += 1

    for s in servicios_cotizacion:
        filas_html += f"""
            <tr>
                <td style="text-align:center;">{item_num}</td>
                <td style="text-align:center;">1</td>
                <td>—</td>
                <td>{s['item']}</td>
                <td style="text-align:center;">Servicio</td>
                <td style="text-align:right;">S/. {s['precio']:.2f}</td>
                <td style="text-align:right;">S/. {s['precio']:.2f}</td>
            </tr>
        """
        item_num += 1

    if not detalles and not servicios_cotizacion:
        filas_html = '<tr><td colspan="7" style="text-align:center;color:#888;">Sin ítems registrados.</td></tr>'

    html = f"""
    <html>
    <head>
    <style>
        @page {{ size: A4; margin: 1.8cm; }}
        body {{ font-family: Helvetica, Arial, sans-serif; color: #222; font-size: 9.5pt; }}

        .header {{ width: 100%; border-bottom: 3px solid #7A0C11; padding-bottom: 12px; margin-bottom: 16px; }}
        .header-empresa {{ font-size: 16pt; font-weight: bold; color: #7A0C11; }}
        .header-empresa-sub {{ font-size: 8pt; color: #666; }}
        .header-doc-num {{ font-size: 13pt; font-weight: bold; color: #222; text-align: right; }}
        .header-doc-fecha {{ font-size: 8pt; color: #666; text-align: right; }}

        table.info {{ width: 100%; margin-bottom: 14px; font-size: 9pt; }}
        table.info td {{ padding: 3px 4px; vertical-align: top; }}
        .label {{ font-size: 7.5pt; color: #888; text-transform: uppercase; letter-spacing: .4px; }}
        .valor {{ font-size: 9.5pt; font-weight: bold; color: #222; }}

        table.detalle {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
        table.detalle th {{ background: #7A0C11; color: #fff; padding: 6px 5px; text-align: left; font-size: 8pt; }}
        table.detalle td {{ padding: 6px 5px; border-bottom: 1px solid #ddd; font-size: 8.5pt; }}

        table.totales {{ width: 280px; float: right; margin-top: 10px; border-collapse: collapse; }}
        table.totales td {{ padding: 4px 8px; font-size: 9.5pt; }}
        table.totales .lbl {{ text-align: right; color: #555; }}
        table.totales .val {{ text-align: right; font-weight: bold; }}
        table.totales .total-final td {{ font-size: 12pt; font-weight: bold; color: #7A0C11; border-top: 2px solid #7A0C11; }}

        .badge-estado {{ display: inline-block; background: #16A34A; color: #fff; padding: 3px 10px;
                          border-radius: 10px; font-size: 8pt; font-weight: bold; }}
        .footer {{ clear: both; margin-top: 50px; font-size: 7.5pt; color: #999; text-align: center;
                   border-top: 1px solid #ddd; padding-top: 8px; }}
    </style>
    </head>
    <body>
        <table class="header">
            <tr>
                <td width="60%">
                    <div class="header-empresa">AutoGest</div>
                    <div class="header-empresa-sub">Sistema de Gestión de Taller Mecánico</div>
                </td>
                <td width="40%">
                    <div class="header-doc-num">ORDEN DE TRABAJO N° {id_orden:05d}</div>
                    <div class="header-doc-fecha">Estado: <span class="badge-estado">COMPLETADA</span></div>
                </td>
            </tr>
        </table>

        <table class="info">
            <tr>
                <td width="25%">
                    <div class="label">Cliente</div>
                    <div class="valor">{c.get('nombre', '—')}</div>
                </td>
                <td width="25%">
                    <div class="label">Placa</div>
                    <div class="valor">{v.get('placa','—')}</div>
                </td>
                <td width="25%">
                    <div class="label">Vehículo</div>
                    <div class="valor">{v.get('marca','')} {v.get('modelo','')}</div>
                </td>
                <td width="25%">
                    <div class="label">Mecánico</div>
                    <div class="valor">{e.get('nombre', '—')}</div>
                </td>
            </tr>
            <tr>
                <td>
                    <div class="label">Fecha de Ingreso</div>
                    <div class="valor">{fecha_ing}</div>
                </td>
                <td>
                    <div class="label">Fecha de Entrega</div>
                    <div class="valor">{fecha_ent}</div>
                </td>
                <td colspan="2"></td>
            </tr>
        </table>

        <table class="detalle">
            <thead>
                <tr>
                    <th style="text-align:center;width:5%;">Ítem</th>
                    <th style="text-align:center;width:7%;">Cant.</th>
                    <th style="width:12%;">Código</th>
                    <th>Descripción</th>
                    <th style="text-align:center;width:10%;">Tipo</th>
                    <th style="text-align:right;width:12%;">P. Unit.</th>
                    <th style="text-align:right;width:12%;">Importe</th>
                </tr>
            </thead>
            <tbody>
                {filas_html}
            </tbody>
        </table>

        <table class="totales">
            <tr><td class="lbl">Sub Total:</td><td class="val">S/. {subtotal:.2f}</td></tr>
            <tr><td class="lbl">I.G.V. (18%):</td><td class="val">S/. {igv:.2f}</td></tr>
            <tr class="total-final"><td class="lbl">TOTAL:</td><td class="val">S/. {total:.2f}</td></tr>
        </table>

        <div class="footer">
            Documento generado por AutoGest — Sistema de Gestión de Taller Mecánico de Trabajo.
        </div>
    </body>
    </html>
    """
    return html