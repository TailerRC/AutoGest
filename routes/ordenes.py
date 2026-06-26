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


def render_ordenes_list(req, usuario, ordenes):
    """Renderiza la lista de órdenes de trabajo."""
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

    # Conteos
    pendientes  = sum(1 for o in ordenes if o.get("estado") == "pendiente")
    en_proceso  = sum(1 for o in ordenes if o.get("estado") == "en_proceso")
    completadas = sum(1 for o in ordenes if o.get("estado") == "completada")
    canceladas  = sum(1 for o in ordenes if o.get("estado") == "cancelada")
    total       = len(ordenes)

    # Gráfico circular con Canvas
    chart_data = {
        "labels": ["Pendientes", "En Proceso", "Completadas", "Canceladas"],
        "data":   [pendientes, en_proceso, completadas, canceladas],
        "colors": ["#F59E0B", "#3B82F6", "#10B981", "#EF4444"],
    }

    grafico = Div(
        Div(
            Div(H2(I(cls="fa-solid fa-chart-pie"), " Resumen de Órdenes"), cls="card-header"),
            Div(
                Div(
                    # Canvas centrado
                    Div(
                        Canvas(id="ordenesChart", style="max-height:200px;max-width:200px;"),
                        # Total en el centro del donut via CSS
                        Div(
                            Div(str(total), style="font-size:1.8rem;font-weight:800;color:var(--brand-primary);line-height:1;"),
                            Div("órdenes", style="font-size:.72rem;color:var(--text-muted);font-weight:500;"),
                            style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;"
                        ),
                        style="position:relative;display:flex;align-items:center;justify-content:center;"
                    ),
                    # Leyenda en 2 columnas
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

    # Tabla
    filas = []
    for o in ordenes:
        # Limpiar fechas — quitar el " 00:00:00" si viene de Oracle
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
                    href=f"/ordenes/{o.get('id_orden', '')}",  # ← va al detalle, no a /editar
                    cls="btn-icon icon-edit",
                    **{"data-tooltip": "Ver y editar"}
                )
            )

        # Badge de orden con hover
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
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Órdenes", "Órdenes de Trabajo", "Base de datos Oracle", contenido)


def render_ordenes_detalle(req, usuario, orden, repuestos):
    """Vista detalle completa — info + estado + repuestos + agregar."""
    id_orden = orden["id_orden"]
    msg  = req.query_params.get("msg", "")
    alert = Div(
        Div(I(cls="fa-solid fa-circle-check"), " Repuesto agregado correctamente.", cls="alert-message"),
        Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
        cls="alert alert-success alert-dismissible"
    ) if msg == "detalle_agregado" else ""

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

    # ── Filas de repuestos ───────────────────────────────────────────
    filas_det = [
        Tr(
            Td(d["nombre_pieza"], style="font-weight:500;"),
            Td(str(d["cantidad"]), style="text-align:center;"),
            Td(f"S/. {d['precio_unitario']:.2f}"),
            Td(f"S/. {d['subtotal']:.2f}",
               style="font-weight:700;color:var(--brand-primary);text-align:right;"),
        )
        for d in detalles
    ]

    # ── Formulario agregar repuesto ──────────────────────────────────
    agregar_form = ""
    if puede_acceder(usuario, "ordenes", "crear"):
        opts = [Option(f"{r['nombre']} (Stock: {r['stock']})", value=str(r["id_pieza"]))
                for r in repuestos]
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
                        Select(*opts, name="id_pieza", required=True),
                        cls="form-group"),
                    Div(Label("Cantidad"),
                        Input(name="cantidad", type="number", min="1", value="1", required=True),
                        cls="form-group"),
                    Div(Label("Precio unitario (S/.)"),
                        Input(name="precio_unitario", type="number", step="0.01",
                              min="0", placeholder="0.00", required=True),
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
            style="margin-top:1.5rem;padding-top:1.5rem;border-top:1px solid var(--border);"
        )

    contenido = Div(
        alert,
        Div(
            # ── Encabezado ──────────────────────────────────────────
            Div(
                Div(
                    H2(I(cls="fa-solid fa-clipboard-list"), f" Orden #{id_orden}"),
                    badge_estado(orden["estado"]),
                    cls="flex gap-2", style="align-items:center;"
                ),
                A(I(cls="fa-solid fa-arrow-left"), " Volver",
                  href="/ordenes", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(
                # ── Datos principales en grid ────────────────────────
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

                # ── Separador ────────────────────────────────────────
                Div(style="margin-top:1.5rem;padding-top:1.5rem;border-top:1px solid var(--border);"),

                # ── Repuestos ────────────────────────────────────────
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
                            Th("Subtotal", style="text-align:right;")
                        )),
                        Tbody(*filas_det) if filas_det else Tbody(
                            Tr(Td("Sin repuestos agregados.", colspan="4", cls="no-data"))
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

                # ── Agregar repuesto (inline, sin segunda card) ──────
                agregar_form,

                cls="card-body"
            ),
            cls="card fade-in"
        ),

        # ── Botón editar orden completa ──────────────────────────────
        Div(
            A(
                I(cls="fa-solid fa-pen"), " Editar datos de la orden",
                href=f"/ordenes/{id_orden}/editar",
                cls="btn btn-secondary"
            ),
            style="margin-top:1rem;"
        ) if puede_acceder(usuario, "ordenes", "editar") else "",

        cls="page-body"
    )
    return layout(req, f"Orden #{id_orden}", f"Orden de Trabajo #{id_orden}",
                  c.get("nombre", ""), contenido)


def render_ordenes_nueva(req, vehiculos, mecanicos):
    """Formulario de nueva orden — mismo estilo que editar."""
    hoy    = date.today().strftime("%Y-%m-%d")
    opts_v = [Option(f"{v['placa']} — {v['marca']} {v['modelo']}",
                     value=str(v["id_vehiculo"])) for v in vehiculos]
    opts_e = [Option(f"{e['nombre']} · {e.get('especialidad','—')}",
                     value=str(e["id_empleado"])) for e in mecanicos]

    form = Form(
        Div(
            Div(Label("Vehículo"),
                Select(Option("-- Seleccionar vehículo --", value=""),
                       *opts_v, name="id_vehiculo", required=True),
                cls="form-group"),
            Div(Label("Mecánico asignado"),
                Select(Option("-- Seleccionar mecánico --", value=""),
                       *opts_e, name="id_empleado", required=True),
                cls="form-group"),
            Div(Label("Fecha de ingreso"),
                Input(name="fecha_ingreso", type="date", value=hoy, required=True),
                cls="form-group"),
            Div(Label("Fecha estimada de entrega"),
                Input(name="fecha_entrega", type="date", required=True),
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
        cls="page-body"
    )
    return layout(req, "Nueva Orden", "Nueva Orden de Trabajo",
                  "Base de datos Oracle", contenido)


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