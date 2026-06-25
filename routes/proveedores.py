"""
routes/proveedores.py
=====================
Vista para Proveedores.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout


def render_proveedores_list(req, usuario, proveedores, q="", linea="todos", page=1, total_pages=1, total_count=0):
    """
    Renderiza el panel de proveedores con búsqueda integrada, filtros por línea,
    paginación numérica responsiva y estilos corporativos.
    """
    filas = []
    for p in proveedores:
        contacto = p.get("contacto", {})
        lineas = p.get("lineas_productos", [])
        
        acciones = []
        if puede_acceder(usuario, "proveedores", "editar"):
            acciones.append(
                A(
                    I(cls="fa-solid fa-pen-to-square"), " Editar",
                    href=f"/proveedores/{p['codigoProveedor']}/editar",
                    cls="btn btn-sm btn-secondary"
                )
            )

        filas.append(Tr(
            Td(
                Span(p.get("codigoProveedor", "—"), cls="font-mono badge badge-gray"),
                data_label="Código"
            ),
            Td(
                Span(p.get("nombreEmpresa", "—"), style="font-weight:600; color:var(--text-primary);"),
                data_label="Razón Social"
            ),
            Td(
                Div(*[Span(l, cls="tag") for l in lineas], cls="tag-list") if lineas else "—",
                data_label="Líneas"
            ),
            Td(
                Div(
                    Div(
                        Span(I(cls="fa-solid fa-phone"), style="margin-right:0.25rem; color:var(--brand-primary); font-size:0.75rem;"),
                        Span(contacto.get("telefono", "—")),
                        style="display:flex; align-items:center; gap:0.25rem; font-weight:500;"
                    ),
                    Div(
                        Span(I(cls="fa-solid fa-envelope"), style="margin-right:0.25rem; color:var(--brand-secondary); font-size:0.75rem;"),
                        Span(contacto.get("email", "—")),
                        style="display:flex; align-items:center; gap:0.25rem; font-size:0.8rem; color:var(--text-muted); margin-top:0.2rem;"
                    )
                ),
                data_label="Contacto"
            ),
            Td(
                Div(*acciones, cls="flex gap-1") if acciones else "—",
                data_label="Acciones"
            )
        ))

    crear_btn = (
        A(
            I(cls="fa-solid fa-plus"), " Nuevo Proveedor",
            href="/proveedores/nuevo",
            cls="btn btn-primary"
        )
        if puede_acceder(usuario, "proveedores", "crear")
        else ""
    )

    tabla = Div(
        Table(
            Thead(Tr(
                Th("Código"),
                Th("Razón Social"),
                Th("Líneas de Producto"),
                Th("Contacto"),
                Th("Acciones")
            )),
            Tbody(*filas) if filas else Tbody(Tr(Td("No se encontraron proveedores con los filtros aplicados.", colspan="5", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    # Panel de Búsqueda y Filtros
    lineas_opciones = ["Todos", "Frenos", "Filtros", "Motor", "Electricidad", "Pintura", "Carrocería", "Herramientas", "Refrigeración"]
    select_options = [
        Option(opt, value=opt if opt != "Todos" else "todos", selected=(linea == (opt if opt != "Todos" else "todos")))
        for opt in lineas_opciones
    ]
    
    filter_form = Form(
        Div(
            Div(
                Label("Búsqueda"),
                Input(name="q", placeholder="Código, razón social o contacto...", value=q),
                cls="form-group"
            ),
            Div(
                Label("Línea de Producto"),
                Select(
                    *select_options,
                    name="linea"
                ),
                cls="form-group"
            ),
            Div(
                Label(style="visibility:hidden;"),
                Div(
                    Button(I(cls="fa-solid fa-magnifying-glass"), " Buscar", type="submit", cls="btn btn-primary"),
                    A(I(cls="fa-solid fa-filter-circle-xmark"), " Limpiar", href="/proveedores", cls="btn btn-secondary"),
                    style="display:flex; gap:0.5rem;"
                ),
                cls="form-group"
            ),
            cls="form-grid",
            style="margin-bottom:0.5rem; align-items: flex-end;"
        ),
        method="get", action="/proveedores",
        cls="filter-card",
        style="padding:1.25rem; background:var(--bg-page); border:1.5px solid var(--border); border-radius:var(--radius); margin-bottom:1.5rem;"
    )

    # Paginación deslizante (máximo 5 páginas visibles)
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
            A(
                str(p),
                href=f"/proveedores?page={p}&q={q}&linea={linea}",
                cls=btn_cls,
                style="min-width:32px; text-align:center;"
            )
        )

    # Paginación Anterior / Siguiente
    if page > 1:
        pag_prev = A(
            I(cls="fa-solid fa-chevron-left"), " Anterior",
            href=f"/proveedores?page={page - 1}&q={q}&linea={linea}",
            cls="btn btn-sm btn-secondary"
        )
    else:
        pag_prev = Span(
            I(cls="fa-solid fa-chevron-left"), " Anterior",
            cls="btn btn-sm btn-secondary disabled",
            style="opacity:0.5; cursor:not-allowed;"
        )
        
    if page < total_pages:
        pag_next = A(
            "Siguiente ", I(cls="fa-solid fa-chevron-right"),
            href=f"/proveedores?page={page + 1}&q={q}&linea={linea}",
            cls="btn btn-sm btn-secondary"
        )
    else:
        pag_next = Span(
            "Siguiente ", I(cls="fa-solid fa-chevron-right"),
            cls="btn btn-sm btn-secondary disabled",
            style="opacity:0.5; cursor:not-allowed;"
        )

    start_item = (page - 1) * 6 + 1 if total_count > 0 else 0
    end_item = min(page * 6, total_count)
    
    paginacion = Div(
        Span(f"Mostrando {start_item}–{end_item} de {total_count} registros", cls="text-muted text-sm"),
        Div(
            pag_prev,
            *page_buttons,
            pag_next,
            cls="paginacion-nav"
        ),
        cls="paginacion-container"
    )

    msg = req.query_params.get("msg", "")
    alert_map = {
        "creado": Div(I(cls="fa-solid fa-circle-check"), " Proveedor registrado exitosamente.", cls="alert alert-success"),
        "editado": Div(I(cls="fa-solid fa-circle-check"), " Proveedor actualizado exitosamente.", cls="alert alert-success"),
    }
    alert = alert_map.get(msg, "")

    contenido = Div(
        alert,
        Div(
            Div(
                H2(I(cls="fa-solid fa-truck"), " Proveedores"),
                Span("MongoDB", cls="db-tag mongo"),
                cls="card-header"
            ),
            Div(
                Div(
                    P("Directorio de proveedores para la cadena de suministro de repuestos.", cls="text-muted text-sm"),
                    crear_btn,
                    cls="flex gap-2",
                    style="justify-content:space-between;align-items:center;margin-bottom:1.5rem;"
                ),
                filter_form,
                tabla,
                paginacion,
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Proveedores", "Gestión de Proveedores", "Base de datos MongoDB", contenido)


def render_proveedores_nuevo(req):
    """
    Renderiza el formulario independiente para crear un proveedor.
    Realiza pre-validaciones del lado del cliente.
    """
    error = req.query_params.get("error", "")
    alert = Div(I(cls="fa-solid fa-circle-exclamation"), f" {error}", cls="alert alert-error") if error else ""

    form = Form(
        alert,
        Div(
            Div(
                Label("Código del Proveedor"),
                Input(name="codigo", value="AUTO", readonly=True, cls="readonly", style="background:#f1f5f9; color:#64748b; font-weight:700;"),
                cls="form-group"
            ),
            Div(
                Label("Razón Social"),
                Input(name="nombre_empresa", placeholder="AutoParts S.A.", required=True),
                cls="form-group"
            ),
            Div(
                Label("Líneas de Producto (separadas por coma)"),
                Input(name="lineas_raw", placeholder="Filtros, Frenos, Motor", required=True),
                cls="form-group"
            ),
            Div(
                Label("Teléfono (9 dígitos)"),
                Input(name="telefono", placeholder="999888777", required=True, type="tel", pattern="[0-9]{9}"),
                cls="form-group"
            ),
            Div(
                Label("Correo Electrónico"),
                Input(name="email", type="email", placeholder="contacto@autoparts.com", required=True),
                cls="form-group"
            ),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/proveedores", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Guardar Proveedor", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/proveedores/crear"
    )

    contenido = Div(
        Div(
            Div(
                H2(I(cls="fa-solid fa-plus"), " Nuevo Proveedor"),
                A("← Volver", href="/proveedores", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nuevo Proveedor", "Nuevo Proveedor", "", contenido)


def render_proveedores_editar(req, proveedor):
    """
    Renderiza el formulario independiente para editar un proveedor.
    """
    error = req.query_params.get("error", "")
    alert = Div(I(cls="fa-solid fa-circle-exclamation"), f" {error}", cls="alert alert-error") if error else ""

    contacto = proveedor.get("contacto", {})
    lineas = ", ".join(proveedor.get("lineas_productos", []))

    form = Form(
        alert,
        Div(
            Div(
                Label("Código del Proveedor"),
                Input(name="codigo", value=proveedor["codigoProveedor"], readonly=True, cls="readonly", style="background:#f1f5f9; color:#64748b; font-weight:700;"),
                cls="form-group"
            ),
            Div(
                Label("Razón Social"),
                Input(name="nombre_empresa", value=proveedor.get("nombreEmpresa", ""), required=True),
                cls="form-group"
            ),
            Div(
                Label("Líneas de Producto"),
                Input(name="lineas_raw", value=lineas, required=True),
                cls="form-group"
            ),
            Div(
                Label("Teléfono (9 dígitos)"),
                Input(name="telefono", value=contacto.get("telefono", ""), required=True, type="tel", pattern="[0-9]{9}"),
                cls="form-group"
            ),
            Div(
                Label("Correo Electrónico"),
                Input(name="email", type="email", value=contacto.get("email", ""), required=True),
                cls="form-group"
            ),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/proveedores", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Actualizar Proveedor", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/proveedores/actualizar"
    )

    contenido = Div(
        Div(
            Div(
                H2(I(cls="fa-solid fa-pen-to-square"), f" Editar Proveedor: {proveedor.get('nombreEmpresa', '')}"),
                A("← Volver", href="/proveedores", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Editar Proveedor", f"Editar Proveedor", "", contenido)
