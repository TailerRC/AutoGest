"""
routes/vehiculos.py — View puro de Vehículos
=============================================
Solo renderiza HTML. Lógica en controllers/vehiculos_ctrl.py.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout

MARCAS = ["Toyota", "Hyundai", "Kia", "Nissan", "Chevrolet", "Honda", "Mazda",
          "Suzuki", "Mitsubishi", "Ford", "Volkswagen", "Renault"]


def render_vehiculos_list(req, usuario, vehiculos, clientes, total, page, per_page):
    """Renderiza la lista de vehículos."""
    msg = req.query_params.get("msg", "")
    alert_map = {
        "creado": Div(
            Div(I(cls="fa-solid fa-circle-check"), " Vehículo registrado correctamente.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        ),
        "editado": Div(
            Div(I(cls="fa-solid fa-circle-check"), " Vehículo actualizado correctamente.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        ),
        "eliminado": Div(
            Div(I(cls="fa-solid fa-trash"), " Vehículo eliminado.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-warning alert-dismissible"
        ),
        "con_ordenes": Div(
            Div(
                I(cls="fa-solid fa-triangle-exclamation"),
                " No se puede eliminar este vehículo porque tiene órdenes de trabajo asociadas.",
                cls="alert-message"
            ),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-error alert-dismissible"
        ),
        "error": Div(
            Div(I(cls="fa-solid fa-circle-exclamation"), " Ocurrió un error al intentar eliminar el vehículo.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-error alert-dismissible"
        ),
    }
    alert = alert_map.get(msg, "")

    # ── Paginación ──────────────────────────────────────────────────
    total_pages = max(1, -(-total // per_page))

    def url_page(p, pp=None):
        pp = pp or per_page
        msg_actual = req.query_params.get("msg", "")
        m = f"&msg={msg_actual}" if msg_actual else ""
        return f"/vehiculos?page={p}&per_page={pp}{m}"

    selector_pp = Div(
        Span("Mostrar", cls="text-muted text-sm"),
        *[
            A(str(n), href=url_page(1, n),
              cls=f"btn btn-sm {'btn-primary' if per_page == n else 'btn-secondary'}")
            for n in (10, 15, 20)
        ],
        Span("por página", cls="text-muted text-sm"),
        cls="flex gap-1", style="align-items:center;"
    )

    paginas = []
    if page > 1:
        paginas.append(A(I(cls="fa-solid fa-chevron-left"), href=url_page(page - 1), cls="btn btn-sm btn-secondary"))
    else:
        paginas.append(Span(I(cls="fa-solid fa-chevron-left"), cls="btn btn-sm btn-secondary", style="opacity:.35;pointer-events:none;"))

    rango_inicio = max(1, page - 2)
    rango_fin    = min(total_pages, rango_inicio + 4)

    if rango_inicio > 1:
        paginas.append(A("1", href=url_page(1), cls="btn btn-sm btn-secondary"))
        if rango_inicio > 2:
            paginas.append(Span("…", cls="text-muted text-sm", style="padding:0 .25rem;"))

    for p in range(rango_inicio, rango_fin + 1):
        paginas.append(
            A(str(p), href=url_page(p),
              cls=f"btn btn-sm {'btn-primary' if p == page else 'btn-secondary'}")
        )

    if rango_fin < total_pages:
        if rango_fin < total_pages - 1:
            paginas.append(Span("…", cls="text-muted text-sm", style="padding:0 .25rem;"))
        paginas.append(A(str(total_pages), href=url_page(total_pages), cls="btn btn-sm btn-secondary"))

    if page < total_pages:
        paginas.append(A(I(cls="fa-solid fa-chevron-right"), href=url_page(page + 1), cls="btn btn-sm btn-secondary"))
    else:
        paginas.append(Span(I(cls="fa-solid fa-chevron-right"), cls="btn btn-sm btn-secondary", style="opacity:.35;pointer-events:none;"))

    barra_paginacion = Div(
        Div(
            Span(
                f"Mostrando {(page-1)*per_page + 1}–{min(page*per_page, total)} de {total} registros",
                cls="text-muted text-sm"
            ),
            selector_pp,
            cls="flex gap-2", style="align-items:center;justify-content:space-between;"
        ),
        Div(*paginas, cls="flex gap-1", style="justify-content:center;align-items:center;margin-top:.75rem;"),
        style="margin-top:1rem;padding-top:1rem;border-top:1px solid var(--border);"
    )

    filas = []
    for v in vehiculos:
        acciones = []
        if puede_acceder(usuario, "vehiculos", "editar"):
            acciones.append(
                A(
                    I(cls="fa-solid fa-pen"),
                    href=f"/vehiculos/{v['id_vehiculo']}/editar",
                    cls="btn-icon icon-edit",
                    **{"data-tooltip": "Editar"}
                )
            )
        nombre_modal = f"{v['placa']} — {v.get('marca', '')} {v.get('modelo', '')}"
        if puede_acceder(usuario, "vehiculos", "eliminar"):
            acciones.append(
                Form(
                    Input(type="hidden", name="id_vehiculo", value=str(v["id_vehiculo"])),
                    Button(
                        I(cls="fa-solid fa-trash"),
                        type="button",
                        cls="btn-icon icon-delete",
                        **{"data-tooltip": "Eliminar"},
                        onclick=(
                            "confirmarEliminar(this, {"
                            "titulo: '¿Eliminar vehículo?',"
                            "mensaje: 'Esta acción no se puede deshacer.',"
                            f"nombre: '{nombre_modal}'"
                            "})"
                        )
                    ),
                    method="post", action="/vehiculos/eliminar"
                )
            )

        # Badge de placa con icono de carrito que aparece al hover
        placa_badge = Div(
            I(cls="fa-solid fa-car placa-car-icon"),
            Span(v.get("placa", "—"), cls="placa-texto"),
            cls="placa-badge"
        )

        filas.append(Tr(
            Td(placa_badge, cls="td-placa"),
            Td(
                Span(f"{v.get('marca', '')} {v.get('modelo', '')}".strip(), cls="vehiculo-nombre"),
                cls=""
            ),
            Td(
                Div(
                    I(cls="fa-solid fa-calendar-days anio-cal-icon"),
                    Span(" " + str(v.get("anio", v.get("año", "—"))), cls="anio-texto"),
                    cls="anio-badge"
                )
            ),
            Td(v.get("nombre_cliente", "—")),
            Td(Div(*acciones, cls="row-actions") if acciones else "—"),
        ))

    tabla = Div(
        Table(
            Thead(Tr(
                Th("Placa"),
                Th("Vehículo"),
                Th("Año"),
                Th("Propietario"),
                Th("Acciones")
            )),
            Tbody(*filas) if filas else Tbody(
                Tr(Td("No hay vehículos registrados.", colspan="5", cls="no-data"))
            ),
        ),
        cls="table-wrap"
    )

    crear_btn = A(
        I(cls="fa-solid fa-plus"), " Nuevo Vehículo",
        href="/vehiculos/nuevo", cls="btn btn-primary"
    ) if puede_acceder(usuario, "vehiculos", "crear") else ""

    contenido = Div(
        Style("""
            /* ── Placa Badge con efecto hover carrito ── */
            .placa-badge {
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
                position: relative;
            }

            .placa-car-icon {
                font-size: .85rem;
                max-width: 0;
                opacity: 0;
                overflow: hidden;
                transition: max-width .25s ease, opacity .2s ease, margin-right .25s ease;
                margin-right: 0;
                color: var(--brand-primary);
            }

            tr:hover .placa-badge {
                background: var(--brand-primary-light);
                border-color: rgba(122,12,17,.3);
                color: var(--brand-primary);
                box-shadow: 0 2px 8px rgba(122,12,17,.12);
            }

            tr:hover .placa-car-icon {
                max-width: 20px;
                opacity: 1;
                margin-right: .4rem;
            }

            /* ── Nombre del vehículo ── */
            .vehiculo-nombre {
                font-weight: 600;
                color: var(--text-primary);
            }

            .td-placa { width: 130px; }
        """),
        alert,
         Div(
            Div(H2(I(cls="fa-solid fa-car"), " Vehículos"), cls="card-header"),
            Div(
                Div(
                    Span(f"{total} registros", cls="text-muted text-sm"),  # ← total, no len()
                    crear_btn,
                    cls="flex gap-2",
                    style="justify-content:space-between;align-items:center;margin-bottom:1rem;"
                ),
                tabla,
                barra_paginacion,  # ← aquí
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Vehículos", "Gestión de Vehículos", "Base de datos Oracle", contenido)

def render_vehiculos_nuevo(req, clientes):
    """Renderiza el formulario de nuevo vehículo."""
    error = req.query_params.get("error", "")
    alert = Div(
        I(cls="fa-solid fa-circle-exclamation"), f" {error}",
        cls="alert alert-error"
    ) if error else ""

    opciones_clientes = [Option(f"{c['nombre']} (DNI: {c['dni']})", value=str(c["id_cliente"])) for c in clientes]

    form = Form(
        alert,
        Div(
            Div(
                Label("Cliente propietario"),
                Select(Option("-- Seleccionar --", value=""), *opciones_clientes, name="id_cliente", required=True),
                cls="form-group"
            ),
            Div(Label("Placa"), Input(name="placa", placeholder="ABC-123", required=True, maxlength="8"), cls="form-group"),
            Div(
                Label("Marca"),
                Select(*[Option(m, value=m) for m in MARCAS], name="marca", required=True),
                cls="form-group"
            ),
            Div(Label("Modelo"), Input(name="modelo", placeholder="Corolla, Accent, Rio...", required=True), cls="form-group"),
            Div(
                Label("Año"),
                Input(name="anio", type="number", min="1990", max="2026", placeholder="2022", required=True),
                cls="form-group"
            ),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/vehiculos", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Guardar Vehículo", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/vehiculos/crear"
    )

    contenido = Div(
        Div(
            Div(
                H2(I(cls="fa-solid fa-car"), " Nuevo Vehículo"),
                A(I(cls="fa-solid fa-arrow-left"), " Volver", href="/vehiculos", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(form, cls="card-body"),
            cls="form-card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nuevo Vehículo", "Nuevo Vehículo", "Vincular a cliente Oracle", contenido)


def render_vehiculos_editar(req, vehiculo, clientes):
    id_vehiculo = vehiculo["id_vehiculo"]
    placa       = vehiculo["placa"].upper()
    msg         = req.query_params.get("msg", "")
    error       = req.query_params.get("error", "")
    """Renderiza el formulario de edición de un vehículo."""
    id_vehiculo = vehiculo["id_vehiculo"]
    opciones = [
        Option(f"{c['nombre']}", value=str(c["id_cliente"]),
               selected=(c["id_cliente"] == vehiculo["id_cliente"]))
        for c in clientes
    ]

    form = Form(
        Div(
            Div(Label("Cliente propietario"), Select(*opciones, name="id_cliente", required=True), cls="form-group"),
            Div(Label("Placa"), Input(name="placa", value=vehiculo["placa"], required=True), cls="form-group"),
            Div(
                Label("Marca"),
                Select(*[Option(m, value=m, selected=(m == vehiculo["marca"])) for m in MARCAS],
                       name="marca", required=True),
                cls="form-group"
            ),
            Div(Label("Modelo"), Input(name="modelo", value=vehiculo["modelo"], required=True), cls="form-group"),
            Div(
                Label("Año"),
                Input(name="anio", type="number",
                      value=str(vehiculo.get("anio", vehiculo.get("año", ""))),
                      min="1990", max="2026", required=True),
                cls="form-group"
            ),
            cls="form-grid"
        ),
        Input(type="hidden", name="id_vehiculo", value=str(id_vehiculo)),
        Div(
            A("Cancelar", href="/vehiculos", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Actualizar", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/vehiculos/actualizar"
    )
    
    alert_foto = ""
    if msg == "fotos_ok":
        alert_foto = Div(
            Div(I(cls="fa-solid fa-circle-check"), " Fotos guardadas correctamente.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        )
    elif error:
        alert_foto = Div(
            Div(I(cls="fa-solid fa-triangle-exclamation"), f" {error}", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-error alert-dismissible"
        )

    seccion_fotos = Div(
        Div(
            H2(I(cls="fa-solid fa-camera"), " Fotos del Vehículo"),
            cls="card-header"
        ),
        Div(
            alert_foto,
            P(
                I(cls="fa-solid fa-circle-info"),
                f" Se crearán como: ",
                Span(f"{placa}_FRONTAL", cls="badge badge-gray font-mono"),
                ", ",
                Span(f"{placa}_LATERAL", cls="badge badge-gray font-mono"),
                ", ",
                Span(f"{placa}_ANGULAR", cls="badge badge-gray font-mono"),
                cls="text-muted text-sm mb-2"
            ),
            Form(
                Input(type="hidden", name="placa", value=placa),
                Div(
                    Div(
                        Label(I(cls="fa-solid fa-car-side"), " Vista Frontal"),
                        Input(type="file", name="foto_frontal", accept="image/*",
                              required=True, id="foto_frontal"),
                        Div(id="preview_frontal", cls="foto-preview"),
                        cls="form-group"
                    ),
                    Div(
                        Label(I(cls="fa-solid fa-car"), " Vista Lateral"),
                        Input(type="file", name="foto_lateral", accept="image/*",
                              required=True, id="foto_lateral"),
                        Div(id="preview_lateral", cls="foto-preview"),
                        cls="form-group"
                    ),
                    Div(
                        Label(I(cls="fa-solid fa-camera-rotate"), " Toma Angular"),
                        Input(type="file", name="foto_angular", accept="image/*",
                              required=True, id="foto_angular"),
                        Div(id="preview_angular", cls="foto-preview"),
                        cls="form-group"
                    ),
                    cls="form-grid"
                ),
                Div(
                    Span(id="fotos-status", cls="text-muted text-sm", style="align-self:center;"),
                    Button(
                        I(cls="fa-solid fa-cloud-arrow-up"), " Subir Fotos",
                        type="submit", id="btn-subir-fotos",
                        cls="btn btn-primary",
                        disabled=True
                    ),
                    cls="form-actions"
                ),
                method="post",
                action=f"/vehiculos/{id_vehiculo}/fotos",
                enctype="multipart/form-data"
            ),
            Script("""
                const ids = ['foto_frontal', 'foto_lateral', 'foto_angular'];

                function verificar() {
                    const listas = ids.filter(id => {
                        const el = document.getElementById(id);
                        return el && el.files && el.files.length > 0;
                    });
                    const btn    = document.getElementById('btn-subir-fotos');
                    const status = document.getElementById('fotos-status');
                    const faltan = ids.length - listas.length;
                    btn.disabled = faltan > 0;
                    status.textContent = faltan === 0
                        ? '✓ Las 3 fotos están listas.'
                        : `Faltan ${faltan} foto(s).`;
                }

                ids.forEach(id => {
                    const input   = document.getElementById(id);
                    const preview = document.getElementById('preview_' + id.replace('foto_', ''));
                    input.addEventListener('change', () => {
                        preview.innerHTML = '';
                        if (input.files[0]) {
                            const img = document.createElement('img');
                            img.src   = URL.createObjectURL(input.files[0]);
                            img.style.cssText = 'width:100%;height:110px;object-fit:cover;border-radius:8px;';
                            preview.appendChild(img);
                        }
                        verificar();
                    });
                });

                document.addEventListener('DOMContentLoaded', verificar);
            """),
            cls="card-body"
        ),
        cls="form-card fade-in", style="margin-top:1.25rem;"
    )

    contenido = Div(
        Div(
            Div(
                H2(I(cls="fa-solid fa-pen"), f" Editar Vehículo #{id_vehiculo}"),
                A(I(cls="fa-solid fa-arrow-left"), " Volver", href="/vehiculos", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(form, cls="card-body"),
            cls="form-card fade-in"
        ),
        seccion_fotos,
        cls="page-body"
    )
    return layout(req, "Editar Vehículo", f"Editar Vehículo #{id_vehiculo}", "", contenido)
