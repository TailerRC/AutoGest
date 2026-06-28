"""
routes/facturas.py — View puro de Facturas
==========================================
Solo renderiza HTML. Lógica en controllers/facturas_ctrl.py.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout, badge_estado, badge_pago
import json

METODOS_PAGO = ["Efectivo", "Tarjeta Débito", "Tarjeta Crédito", "Billetera Electrónica"]


def render_facturas_list(req, usuario, facturas):
    msg = req.query_params.get("msg", "")
    alert_map = {
        "creado": Div(
            Div(I(cls="fa-solid fa-circle-check"), " Factura generada correctamente.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        ),
        "actualizado": Div(
            Div(I(cls="fa-solid fa-circle-check"), " Estado de factura actualizado.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        ),
    }
    alert = alert_map.get(msg, "")

    # Métricas
    total_cobrado   = sum(f.get("total", 0) for f in facturas if f.get("estado_pago") == "pagada")
    total_pendiente = sum(f.get("total", 0) for f in facturas if f.get("estado_pago") == "pendiente")
    pagadas         = sum(1 for f in facturas if f.get("estado_pago") == "pagada")
    pendientes      = sum(1 for f in facturas if f.get("estado_pago") == "pendiente")
    total           = len(facturas)

    # Conteo por método de pago
    metodos_count = {m: 0 for m in METODOS_PAGO}
    for f in facturas:
        m = f.get("metodo_pago", "")
        if m in metodos_count:
            metodos_count[m] += 1

    colores_metodo = {
        "Efectivo":             "#10B981",
        "Tarjeta Débito":       "#3B82F6",
        "Tarjeta Crédito":      "#8B5CF6",
        "Billetera Electrónica":"#F59E0B",
    }
    iconos_metodo = {
        "Efectivo":             "fa-money-bill-wave",
        "Tarjeta Débito":       "fa-credit-card",
        "Tarjeta Crédito":      "fa-credit-card",
        "Billetera Electrónica":"fa-mobile-screen",
    }

    # ── Gráfico donut estado + gráfico métodos de pago ──────────────
    grafico = Div(
        Div(
            Div(H2(I(cls="fa-solid fa-chart-pie"), " Resumen de Facturación"), cls="card-header"),
            Div(
                Div(
                    # ── Donut estado ─────────────────────────────────
                    Div(
                        Div(
                            Div(
                                Canvas(id="facturasEstadoChart", style="max-height:180px;max-width:180px;"),
                                Div(
                                    Div(str(total), style="font-size:1.6rem;font-weight:800;color:var(--brand-primary);line-height:1;"),
                                    Div("facturas", style="font-size:.7rem;color:var(--text-muted);"),
                                    style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;"
                                ),
                                style="position:relative;display:flex;align-items:center;justify-content:center;"
                            ),
                            # Leyenda estado
                            Div(
                                Div(
                                    Div(style="width:10px;height:10px;border-radius:3px;background:#10B981;flex-shrink:0;"),
                                    Div(
                                        Div("Pagadas", style="font-size:.72rem;color:var(--text-muted);"),
                                        Div(str(pagadas), style="font-size:1.3rem;font-weight:800;color:var(--text-primary);line-height:1;"),
                                    ),
                                    style="display:flex;align-items:center;gap:.5rem;"
                                ),
                                Div(
                                    Div(style="width:10px;height:10px;border-radius:3px;background:#F59E0B;flex-shrink:0;"),
                                    Div(
                                        Div("Pendientes", style="font-size:.72rem;color:var(--text-muted);"),
                                        Div(str(pendientes), style="font-size:1.3rem;font-weight:800;color:var(--text-primary);line-height:1;"),
                                    ),
                                    style="display:flex;align-items:center;gap:.5rem;"
                                ),
                                Div(style="width:100%;height:1px;background:var(--border);margin:.4rem 0;"),
                                Div(
                                    Div("Cobrado", style="font-size:.72rem;color:var(--text-muted);"),
                                    Div(f"S/. {total_cobrado:,.2f}", style="font-size:1rem;font-weight:800;color:#10B981;line-height:1;"),
                                    style="display:flex;flex-direction:column;gap:.1rem;"
                                ),
                                Div(
                                    Div("Por cobrar", style="font-size:.72rem;color:var(--text-muted);"),
                                    Div(f"S/. {total_pendiente:,.2f}", style="font-size:1rem;font-weight:800;color:#F59E0B;line-height:1;"),
                                    style="display:flex;flex-direction:column;gap:.1rem;"
                                ),
                                style="display:flex;flex-direction:column;gap:.7rem;"
                            ),
                            style="display:flex;align-items:center;gap:1.5rem;"
                        ),
                        style="flex:1;padding-right:2rem;border-right:1px solid var(--border);"
                    ),

                    # ── Métodos de pago ──────────────────────────────
                    Div(
                        Div(
                            I(cls="fa-solid fa-wallet", style="color:var(--brand-secondary);"),
                            " Métodos de Pago",
                            style="font-size:.78rem;font-weight:700;color:var(--text-primary);"
                                  "text-transform:uppercase;letter-spacing:.05em;"
                                  "display:flex;align-items:center;gap:.4rem;margin-bottom:1rem;"
                        ),
                        *[
                            Div(
                                Div(
                                    I(cls=f"fa-solid {iconos_metodo[m]}",
                                      style=f"color:{colores_metodo[m]};font-size:.9rem;width:20px;text-align:center;"),
                                    Span(m, style="font-size:.82rem;color:var(--text-primary);font-weight:500;"),
                                    style="display:flex;align-items:center;gap:.5rem;flex:1;"
                                ),
                                Div(
                                    Div(
                                        style=f"height:6px;border-radius:3px;"
                                              f"background:{colores_metodo[m]};"
                                              f"width:{max(4, int(metodos_count[m]/max(total,1)*100))}%;"
                                              f"min-width:4px;transition:width .3s ease;"
                                    ),
                                    style="flex:1;background:var(--border);border-radius:3px;height:6px;margin:0 .75rem;"
                                ),
                                Span(str(metodos_count[m]),
                                     style=f"font-size:.85rem;font-weight:700;color:{colores_metodo[m]};"
                                           f"min-width:20px;text-align:right;"),
                                style="display:flex;align-items:center;margin-bottom:.65rem;"
                            )
                            for m in METODOS_PAGO
                        ],
                        style="flex:1;padding-left:2rem;"
                    ),

                    style="display:flex;align-items:center;"
                ),
                cls="card-body", style="padding:1.75rem;"
            ),
            cls="card fade-in"
        ),
        Script(src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"),
        Script(f"""
            document.addEventListener('DOMContentLoaded', function() {{
                const ctx = document.getElementById('facturasEstadoChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['Pagadas', 'Pendientes'],
                        datasets: [{{
                            data: [{pagadas}, {pendientes}],
                            backgroundColor: ['#10B981', '#F59E0B'],
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

    # ── Tabla ────────────────────────────────────────────────────────
    filas = []
    for f in facturas:
        fecha = str(f.get("fecha", "—")).split(" ")[0]

        factura_badge = Div(
            I(cls="fa-solid fa-file-invoice factura-icon"),
            Span(f"F-{f.get('id_factura', '—'):04d}" if isinstance(f.get('id_factura'), int) else f"#{f.get('id_factura','—')}",
                 cls="factura-id-texto"),
            cls="factura-id-badge"
        )

        acciones = [
            A(
                I(cls="fa-solid fa-eye"),
                href=f"/facturas/{f.get('id_factura', '')}",
                cls="btn-icon icon-view",
                **{"data-tooltip": "Ver detalle"}
            )
        ]
        if puede_acceder(usuario, "facturas", "editar") and f.get("estado_pago") == "pendiente":
            acciones.append(
                Form(
                    Input(type="hidden", name="id_factura", value=str(f.get("id_factura", ""))),
                    Input(type="hidden", name="estado_pago", value="pagada"),
                    Button(
                        I(cls="fa-solid fa-circle-check"),
                        type="submit",
                        cls="btn-icon icon-edit",
                        style="background:var(--green-bg);color:var(--green);border-color:rgba(16,185,129,.2);",
                        **{"data-tooltip": "Marcar pagada"}
                    ),
                    method="post", action="/facturas/cambiar-estado"
                )
            )

        filas.append(Tr(
            Td(factura_badge, cls="td-factura-id"),
            Td(f.get("nombre_cliente", "—")),
            Td(Span(f.get("placa", "—"), cls="badge badge-gray font-mono")),
            Td(Span(fecha, cls="fecha-cell")),
            Td(
                Span(f"S/. {f.get('total', 0):.2f}",
                     style="font-weight:700;color:var(--brand-primary);font-family:monospace;")
            ),
            Td(badge_pago(f.get("metodo_pago", ""))),
            Td(badge_estado(f.get("estado_pago", ""))),
            Td(Div(*acciones, cls="row-actions")),
        ))

    crear_btn = A(
        I(cls="fa-solid fa-plus"), " Generar Factura",
        href="/facturas/nueva", cls="btn btn-primary"
    ) if puede_acceder(usuario, "facturas", "crear") else ""

    tabla = Div(
        Table(
            Thead(Tr(
                Th("N° Factura"), Th("Cliente"), Th("Placa"), Th("Fecha"),
                Th("Total"), Th("Método"), Th("Estado"), Th("Acciones")
            )),
            Tbody(*filas) if filas else Tbody(
                Tr(Td("No hay facturas registradas.", colspan="8", cls="no-data"))
            ),
        ),
        cls="table-wrap"
    )

    contenido = Div(
        Style("""
            .factura-id-badge {
                display: inline-flex;
                align-items: center;
                gap: 0;
                background: var(--brand-secondary-light);
                border: 1.5px solid #c8d4db;
                border-radius: 8px;
                padding: .4rem .65rem;
                font-family: monospace;
                font-size: .82rem;
                font-weight: 700;
                color: var(--brand-secondary);
                letter-spacing: .04em;
                overflow: hidden;
                white-space: nowrap; 
                transition: background .2s, border-color .2s, color .2s, box-shadow .2s;
            }
            .factura-icon {
                font-size: .85rem;
                max-width: 0;
                opacity: 0;
                overflow: hidden;
                transition: max-width .25s ease, opacity .2s ease, margin-right .25s ease;
                margin-right: 0;
                color: var(--brand-primary);
            }
            tr:hover .factura-id-badge {
                background: var(--brand-primary-light);
                border-color: rgba(122,12,17,.3);
                color: var(--brand-primary);
                box-shadow: 0 2px 8px rgba(122,12,17,.12);
            }
            tr:hover .factura-icon {
                max-width: 20px;
                opacity: 1;
                margin-right: .4rem;
            }
            .td-factura-id { width: 110px; white-space: nowrap; }
            .fecha-cell {
                font-size: .82rem;
                font-family: monospace;
                color: var(--text-secondary);
            }
        """),
        alert,
        grafico,
        Div(
            Div(H2(I(cls="fa-solid fa-file-invoice"), " Facturas"), cls="card-header"),
            Div(
                Div(
                    Span(f"{total} facturas", cls="text-muted text-sm"),
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
    return layout(req, "Facturas", "Gestión de Facturas", "Base de datos Oracle", contenido)


def render_facturas_nueva(req, ordenes):
    error = req.query_params.get("error", "")
    alert = Div(
        I(cls="fa-solid fa-circle-exclamation"), f" {error}",
        cls="alert alert-error"
    ) if error else ""

    if not ordenes:
        contenido = Div(
            Div(
                Div(H2(I(cls="fa-solid fa-file-invoice"), " Generar Factura"), cls="card-header"),
                Div(
                    Div(
                        I(cls="fa-solid fa-circle-info"),
                        " Todas las órdenes completadas ya tienen factura generada.",
                        cls="alert alert-info"
                    ),
                    A(I(cls="fa-solid fa-arrow-left"), " Volver a Facturas",
                      href="/facturas", cls="btn btn-secondary"),
                    cls="card-body"
                ),
                cls="form-card fade-in"
            ),
            cls="page-body"
        )
        return layout(req, "Nueva Factura", "Generar Factura", "", contenido)

    opts_o = [
        Option(f"Orden #{o['id_orden']} — {o.get('nombre_cliente','?')} ({o['placa']})",
               value=str(o["id_orden"]))
        for o in ordenes
    ]

    form = Form(
        alert,
        Div(
            Div(Label("Orden de Trabajo"),
                Select(*opts_o, name="id_orden", required=True),
                cls="form-group"),
            Div(Label("Total (S/.)"),
                Input(name="total", type="number", step="0.01", min="0",
                      placeholder="0.00", required=True),
                cls="form-group"),
            Div(Label("Método de Pago"),
                Select(*[Option(m, value=m) for m in METODOS_PAGO],
                       name="metodo_pago", required=True),
                cls="form-group"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/facturas", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Generar Factura",
                   type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/facturas/crear"
    )

    contenido = Div(
        Div(
            Div(
                H2(I(cls="fa-solid fa-file-invoice"), " Generar Nueva Factura"),
                A(I(cls="fa-solid fa-arrow-left"), " Volver",
                  href="/facturas", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(form, cls="card-body"),
            cls="form-card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nueva Factura", "Generar Nueva Factura", "Base de datos Oracle", contenido)


def render_facturas_detalle(req, factura):
    usuario    = req.session.get("usuario")
    id_factura = factura["id_factura"]
    msg   = req.query_params.get("msg", "")
    alert = Div(
        Div(I(cls="fa-solid fa-circle-check"), " Estado actualizado correctamente.", cls="alert-message"),
        Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
        cls="alert alert-success alert-dismissible"
    ) if msg == "actualizado" else ""

    fecha = str(factura.get("fecha", "—")).split(" ")[0]

    cambiar_estado = ""
    if puede_acceder(usuario, "facturas", "editar"):
        opts = [
            Option("Pendiente", value="pendiente", selected=(factura["estado_pago"] == "pendiente")),
            Option("Pagada",    value="pagada",    selected=(factura["estado_pago"] == "pagada")),
        ]
        cambiar_estado = Form(
            Input(type="hidden", name="id_factura", value=str(id_factura)),
            Div(
                Select(*opts, name="estado_pago", style="width:auto;min-width:130px;"),
                Button(I(cls="fa-solid fa-rotate"), " Actualizar",
                       type="submit", cls="btn btn-primary btn-sm"),
                cls="flex gap-1", style="align-items:center;"
            ),
            method="post", action="/facturas/cambiar-estado"
        )

    # Icono y color por método de pago
    icono_metodo = {
        "Efectivo":              "fa-money-bill-wave",
        "Tarjeta Débito":        "fa-credit-card",
        "Tarjeta Crédito":       "fa-credit-card",
        "Billetera Electrónica": "fa-mobile-screen",
    }.get(factura.get("metodo_pago", ""), "fa-wallet")

    contenido = Div(
        alert,
        Div(
            Div(
                Div(
                    H2(I(cls="fa-solid fa-file-invoice"), f" Factura F-{id_factura:04d}"),
                    Span(I(cls="fa-solid fa-database"), " Oracle",
                         cls="badge badge-brand", style="font-size:.7rem;"),
                    cls="flex gap-2", style="align-items:center;"
                ),
                Div(
                    badge_estado(factura["estado_pago"]),
                    A(I(cls="fa-solid fa-arrow-left"), " Volver",
                      href="/facturas", cls="btn btn-secondary btn-sm"),
                    cls="flex gap-1", style="align-items:center;"
                ),
                cls="card-header"
            ),
            Div(
                Div(
                    # N° Factura
                    Div(
                        Div(I(cls="fa-solid fa-hashtag",
                              style="color:var(--brand-secondary);font-size:.8rem;"),
                            " N° FACTURA",
                            style="font-size:.7rem;font-weight:700;color:var(--text-muted);"
                                  "text-transform:uppercase;letter-spacing:.06em;"
                                  "display:flex;align-items:center;gap:.3rem;margin-bottom:.3rem;"),
                        Div(f"F-{id_factura:04d}",
                            style="font-weight:700;font-size:1.1rem;font-family:monospace;"),
                        cls="detail-item"
                    ),
                    # Orden
                    Div(
                        Div(I(cls="fa-solid fa-clipboard-list",
                              style="color:var(--brand-secondary);font-size:.8rem;"),
                            " ORDEN",
                            style="font-size:.7rem;font-weight:700;color:var(--text-muted);"
                                  "text-transform:uppercase;letter-spacing:.06em;"
                                  "display:flex;align-items:center;gap:.3rem;margin-bottom:.3rem;"),
                        Div(f"#{factura['id_orden']}",
                            style="font-weight:600;font-size:.95rem;"),
                        cls="detail-item"
                    ),
                    # Fecha
                    Div(
                        Div(I(cls="fa-solid fa-calendar",
                              style="color:var(--brand-secondary);font-size:.8rem;"),
                            " FECHA",
                            style="font-size:.7rem;font-weight:700;color:var(--text-muted);"
                                  "text-transform:uppercase;letter-spacing:.06em;"
                                  "display:flex;align-items:center;gap:.3rem;margin-bottom:.3rem;"),
                        Div(fecha, style="font-weight:600;font-family:monospace;"),
                        cls="detail-item"
                    ),
                    # Total
                    Div(
                        Div(I(cls="fa-solid fa-sack-dollar",
                              style="color:var(--brand-secondary);font-size:.8rem;"),
                            " TOTAL",
                            style="font-size:.7rem;font-weight:700;color:var(--text-muted);"
                                  "text-transform:uppercase;letter-spacing:.06em;"
                                  "display:flex;align-items:center;gap:.3rem;margin-bottom:.3rem;"),
                        Div(f"S/. {factura['total']:.2f}",
                            style="font-weight:800;font-size:1.4rem;color:var(--brand-primary);"
                                  "font-family:monospace;"),
                        cls="detail-item"
                    ),
                    # Método de pago
                    Div(
                        Div(I(cls=f"fa-solid {icono_metodo}",
                              style="color:var(--brand-secondary);font-size:.8rem;"),
                            " MÉTODO DE PAGO",
                            style="font-size:.7rem;font-weight:700;color:var(--text-muted);"
                                  "text-transform:uppercase;letter-spacing:.06em;"
                                  "display:flex;align-items:center;gap:.3rem;margin-bottom:.3rem;"),
                        Div(badge_pago(factura["metodo_pago"])),
                        cls="detail-item"
                    ),
                    # Estado
                    Div(
                        Div(I(cls="fa-solid fa-rotate",
                              style="color:var(--brand-secondary);font-size:.8rem;"),
                            " ESTADO",
                            style="font-size:.7rem;font-weight:700;color:var(--text-muted);"
                                  "text-transform:uppercase;letter-spacing:.06em;"
                                  "display:flex;align-items:center;gap:.3rem;margin-bottom:.3rem;"),
                        Div(cambiar_estado if cambiar_estado else badge_estado(factura["estado_pago"])),
                        cls="detail-item"
                    ),
                    cls="detail-grid"
                ),
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, f"Factura F-{id_factura:04d}",
                  f"Factura F-{id_factura:04d}", "", contenido)