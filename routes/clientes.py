"""
routes/clientes.py — View puro de Clientes
==========================================
Solo contiene funciones de render HTML.
Toda la lógica está en controllers/clientes_ctrl.py y services/clientes_svc.py.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout, no_perm, badge_estado


def render_clientes_list(req, usuario, clientes, total, page, per_page):
    """Renderiza la lista de clientes."""
    msg = req.query_params.get("msg", "")
    alert_map = {
        "creado": Div(
            Div(I(cls="fa-solid fa-circle-check"), " Cliente creado correctamente.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        ),
        "editado": Div(
            Div(I(cls="fa-solid fa-circle-check"), " Cliente actualizado correctamente.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        ),
        "eliminado": Div(
            Div(I(cls="fa-solid fa-trash"), " Cliente eliminado.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-warning alert-dismissible"
        ),
        "con_vehiculos": Div(
            Div(
                I(cls="fa-solid fa-triangle-exclamation"),
                " No se puede eliminar este cliente porque tiene vehículos registrados. Elimina primero sus vehículos.",
                cls="alert-message"
            ),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-error alert-dismissible"
        ),
        "error": Div(
            Div(I(cls="fa-solid fa-circle-exclamation"), " Ocurrió un error al intentar eliminar el cliente.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-error alert-dismissible"
        ),
    }
    alert = alert_map.get(msg, "")
    # ── Paginación ──────────────────────────────────────────────────
    total_pages = max(1, -(-total // per_page))  # ceil division

    def url_page(p, pp=None):
        pp = pp or per_page
        msg_actual = req.query_params.get("msg", "")
        m = f"&msg={msg_actual}" if msg_actual else ""
        return f"/clientes?page={p}&per_page={pp}{m}"

    # Selector de registros por página
    selector_pp = Div(
        Span("Mostrar", cls="text-muted text-sm"),
        *[
            A(str(n),
              href=url_page(1, n),
              cls=f"btn btn-sm {'btn-primary' if per_page == n else 'btn-secondary'}"
            )
            for n in (10, 15, 20)
        ],
        Span("por página", cls="text-muted text-sm"),
        cls="flex gap-1", style="align-items:center;"
    )
    # Botones de páginas
    paginas = []
    # Anterior
    if page > 1:
        paginas.append(A(I(cls="fa-solid fa-chevron-left"), href=url_page(page - 1), cls="btn btn-sm btn-secondary"))
    else:
        paginas.append(Span(I(cls="fa-solid fa-chevron-left"), cls="btn btn-sm btn-secondary", style="opacity:.35;pointer-events:none;"))

    # Números de página (máx 5 visibles)
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

    # Siguiente
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
    for c in clientes:
        acciones = []
        if puede_acceder(usuario, "clientes", "editar"):
            acciones.append(
                A(
                    I(cls="fa-solid fa-pen"),
                    href=f"/clientes/{c['id_cliente']}/editar",
                    cls="btn-icon icon-edit",
                    **{"data-tooltip": "Editar"}
                )
            )
        if puede_acceder(usuario, "clientes", "eliminar"):
            acciones.append(
                Form(
                    Input(type="hidden", name="id_cliente", value=str(c["id_cliente"])),
                    Button(
                        I(cls="fa-solid fa-trash"),
                        type="button",
                        cls="btn-icon icon-delete",
                        **{"data-tooltip": "Eliminar"},
                        onclick=(
                            "confirmarEliminar(this, {"
                            "titulo: '¿Eliminar cliente?',"
                            "mensaje: 'Esta acción no se puede deshacer.',"
                            f"nombre: '{c['nombre']}'"
                            "})"
                        )
                    ),
                    method="post", action="/clientes/eliminar"
                )
            )

        # Badge de ID con icono de persona al hover
        id_badge = Div(
            I(cls="fa-solid fa-user cliente-user-icon"),
            Span(f"#{c['id_cliente']}", cls="cliente-id-texto"),
            cls="cliente-id-badge"
        )

        filas.append(Tr(
            Td(id_badge, cls="td-cliente-id"),
            Td(c["nombre"]),
            Td(c["dni"]),
            Td(c["telefono"]),
            Td(c["email"]),
            Td(Div(*acciones, cls="row-actions") if acciones else "—"),
        ))

    tabla = Div(
        Table(
            Thead(Tr(Th("#"), Th("Nombre"), Th("DNI"), Th("Teléfono"), Th("Email"), Th("Acciones"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("No hay clientes registrados.", colspan="6", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    crear_btn = A(
        I(cls="fa-solid fa-plus"), " Nuevo Cliente",
        href="/clientes/nuevo", cls="btn btn-primary"
    ) if puede_acceder(usuario, "clientes", "crear") else ""

    contenido = Div(
        Style("""
            /* ── Cliente ID Badge con efecto hover persona ── */
            .cliente-id-badge {
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

            .cliente-user-icon {
                font-size: .85rem;
                max-width: 0;
                opacity: 0;
                overflow: hidden;
                transition: max-width .25s ease, opacity .2s ease, margin-right .25s ease;
                margin-right: 0;
                color: var(--brand-primary);
            }

            tr:hover .cliente-id-badge {
                background: var(--brand-primary-light);
                border-color: rgba(122,12,17,.3);
                color: var(--brand-primary);
                box-shadow: 0 2px 8px rgba(122,12,17,.12);
            }

            tr:hover .cliente-user-icon {
                max-width: 20px;
                opacity: 1;
                margin-right: .4rem;
            }

            .td-cliente-id { width: 80px; }
        """),
        alert,
        Div(
            Div(H2(I(cls="fa-solid fa-users"), " Clientes"), cls="card-header"),
            Div(
                Div(
                    Span(f"{total} registros", cls="text-muted text-sm"),
                    crear_btn,
                    cls="flex gap-2", style="justify-content:space-between;align-items:center;margin-bottom:1rem;"
                ),
                tabla,
                barra_paginacion,  # ← aquí
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Clientes", "Gestión de Clientes", "Añadir, Eliminar y Agregar Clientes", contenido)


def render_clientes_nuevo(req):
    """Renderiza el formulario de nuevo cliente."""
    error = req.query_params.get("error", "")
    alert = Div(
        I(cls="fa-solid fa-circle-exclamation"), f" {error}",
        cls="alert alert-error"
    ) if error else ""

    form = Form(
        alert,
        Div(
            Div(Label("Nombre completo"), Input(name="nombre", placeholder="Carlos Mendoza Rivera", required=True), cls="form-group"),
            Div(Label("DNI"), Input(name="dni", placeholder="72345678", maxlength="8", required=True), cls="form-group"),
            Div(Label("Teléfono"), Input(name="telefono", placeholder="987654321", required=True, minlength="9",maxlength="9",pattern="[0-9]{9}"), cls="form-group"),
            Div(Label("Email"), Input(name="email", type="email", placeholder="cliente@email.com", required=True), cls="form-group"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/clientes", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Guardar Cliente", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/clientes/crear"
    )

    contenido = Div(
        Div(
            Div(
                H2(I(cls="fa-solid fa-user-plus"), " Nuevo Cliente"),
                A(I(cls="fa-solid fa-arrow-left"), " Volver", href="/clientes", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(form, cls="card-body"),
            cls="form-card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nuevo Cliente", "Nuevo Cliente", "Añadir, Eliminar y Agregar Empleados", contenido)


def render_clientes_editar(req, cliente):
    """Renderiza el formulario de edición de un cliente existente."""
    id_cliente = cliente["id_cliente"]
    form = Form(
        Div(
            Div(Label("Nombre completo"), Input(name="nombre", value=cliente["nombre"], required=True), cls="form-group"),
            Div(Label("DNI"), Input(name="dni", value=cliente["dni"], maxlength="8", required=True), cls="form-group"),
            Div(Label("Teléfono"), Input(name="telefono", value=cliente["telefono"], required=True), cls="form-group"),
            Div(Label("Email"), Input(name="email", type="email", value=cliente["email"], required=True), cls="form-group"),
            cls="form-grid"
        ),
        Input(type="hidden", name="id_cliente", value=str(id_cliente)),
        Div(
            A("Cancelar", href="/clientes", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Actualizar", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/clientes/actualizar"
    )

    contenido = Div(
        Div(
            Div(
                H2(I(cls="fa-solid fa-pen"), f" Editar Cliente #{id_cliente}"),
                A(I(cls="fa-solid fa-arrow-left"), " Volver", href="/clientes", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(form, cls="card-body"),
            cls="form-card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Editar Cliente", f"Editar Cliente #{id_cliente}", "", contenido)