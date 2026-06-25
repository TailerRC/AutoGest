"""
routes/cotizaciones.py
======================
Vista para Cotizaciones.
"""
import json
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout, badge_estado

def render_cotizaciones_list(req, usuario, cotizaciones, q="", estado="todos", orden="fecha_desc", page=1, total_pages=1, total_count=0):
    """
    Renderiza la vista principal del listado de cotizaciones con filtros, búsqueda y paginación.
    """
    filas = []

    for c in cotizaciones:
        servicios = c.get("servicios_repuestos", [])

        # Mostrar la cantidad consolidada de ítems para un diseño minimalista
        num_items = len(servicios)
        items_str = f"{num_items} ítem" if num_items == 1 else f"{num_items} ítems"

        estado_badge = badge_estado(
            "Vigente" if c.get("vigente", False) else "Vencida"
        )

        # Cada celda Td incluye su data_label para la transformación responsive a móviles
        filas.append(
            Tr(
                Td(
                    Span(
                        c.get("codigoCotizacion", "—"),
                        cls="font-mono badge badge-gray"
                    ),
                    data_label="Código"
                ),
                Td(c.get("cliente_str", "—"), data_label="Cliente"),
                Td(c.get("vehiculo_str", "—"), style="white-space:nowrap;", data_label="Vehículo"),
                Td(c.get("fecha_validez_str", "—"), data_label="Válido Hasta"),
                Td(estado_badge, data_label="Estado"),
                Td(items_str, data_label="Items"),
                Td(
                    f"S/. {c.get('total', 0):.2f}",
                    style="font-weight:700; color:var(--accent); white-space:nowrap;",
                    data_label="Total"
                ),
                Td(
                    A(
                        I(cls="fa-solid fa-eye"), " Ver Detalle",
                        href=f"/cotizaciones/{c['codigoCotizacion']}",
                        cls="btn btn-sm btn-secondary"
                    ),
                    data_label="Acciones"
                )
            )
        )

    crear_btn = (
        A(
            I(cls="fa-solid fa-plus"), " Nueva Cotización",
            href="/cotizaciones/nueva",
            cls="btn btn-primary"
        )
        if puede_acceder(usuario, "cotizaciones", "crear")
        else ""
    )

    tabla = Div(
        Table(
            Thead(
                Tr(
                    Th("Código"),
                    Th("Cliente"),
                    Th("Vehículo"),
                    Th("Válido Hasta"),
                    Th("Estado"),
                    Th("Items"),
                    Th("Total"),
                    Th("Acciones")
                )
            ),
            Tbody(*filas)
            if filas
            else Tbody(
                Tr(
                    Td(
                        "No se encontraron cotizaciones con los filtros aplicados.",
                        colspan="8",
                        cls="no-data"
                    )
                )
            ),
        ),
        cls="table-wrap"
    )

    # Panel de Búsqueda y Filtros Corporativo
    filter_form = Form(
        Div(
            Div(
                Label("Búsqueda"),
                Input(name="q", placeholder="Código, cliente, placa, marca o modelo...", value=q),
                cls="form-group"
            ),
            Div(
                Label("Estado"),
                Select(
                    Option("Todos", value="todos", selected=(estado == "todos")),
                    Option("Vigente", value="vigente", selected=(estado == "vigente")),
                    Option("Vencida", value="vencida", selected=(estado == "vencida")),
                    name="estado"
                ),
                cls="form-group"
            ),
            Div(
                Label("Ordenar por"),
                Select(
                    Option("Fecha (Recientes primero)", value="fecha_desc", selected=(orden == "fecha_desc")),
                    Option("Fecha (Antiguas primero)", value="fecha_asc", selected=(orden == "fecha_asc")),
                    Option("Total (Mayor a menor)", value="total_desc", selected=(orden == "total_desc")),
                    Option("Total (Menor a mayor)", value="total_asc", selected=(orden == "total_asc")),
                    name="orden"
                ),
                cls="form-group"
            ),
            Div(
                Label(style="visibility:hidden;"),
                Div(
                    Button(I(cls="fa-solid fa-magnifying-glass"), " Buscar", type="submit", cls="btn btn-primary"),
                    A(I(cls="fa-solid fa-filter-circle-xmark"), " Limpiar", href="/cotizaciones", cls="btn btn-secondary"),
                    style="display:flex; gap:0.5rem;"
                ),
                cls="form-group"
            ),
            cls="form-grid",
            style="margin-bottom:0.5rem; align-items: flex-end;"
        ),
        method="get", action="/cotizaciones",
        cls="filter-card",
        style="padding:1.25rem; background:var(--bg-page); border:1.5px solid var(--border); border-radius:var(--radius); margin-bottom:1.5rem;"
    )

    # Generación de botones de páginas numeradas individuales (máximo 5 visibles alrededor de la actual)
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
                href=f"/cotizaciones?page={p}&q={q}&estado={estado}&orden={orden}",
                cls=btn_cls,
                style="min-width:32px; text-align:center;"
            )
        )

    # Paginación Anterior / Siguiente
    if page > 1:
        pag_prev = A(
            I(cls="fa-solid fa-chevron-left"), " Anterior",
            href=f"/cotizaciones?page={page - 1}&q={q}&estado={estado}&orden={orden}",
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
            href=f"/cotizaciones?page={page + 1}&q={q}&estado={estado}&orden={orden}",
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
            style="display:flex; align-items:center; gap:0.25rem;"
        ),
        style="display:flex; justify-content:space-between; align-items:center; margin-top:1.5rem; padding-top:1rem; border-top:1.5px solid var(--border);"
    )

    msg = req.query_params.get("msg", "")

    alert = (
        Div(
            I(cls="fa-solid fa-circle-check"), " Cotización generada exitosamente.",
            cls="alert alert-success"
        )
        if msg == "creado"
        else ""
    )

    contenido = Div(
        alert,
        Div(
            Div(
                H2(I(cls="fa-solid fa-file-invoice-dollar"), " Cotizaciones"),
                Span("MongoDB", cls="db-tag mongo"),
                cls="card-header"
            ),
            Div(
                Div(
                    P(
                        "Gestión de proformas y cotizaciones pre-servicio en base de datos NoSQL.",
                        cls="text-muted text-sm"
                    ),
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

    return layout(
        req,
        "Cotizaciones",
        "Gestión de Cotizaciones",
        "Base de datos MongoDB",
        contenido
    )

def render_cotizaciones_nueva(req, clientes, vehiculos):
    """
    Renderiza la vista del formulario dinámico de nueva cotización.
    """
    error = req.query_params.get("error", "")
    alert = Div(I(cls="fa-solid fa-circle-exclamation"), f" {error}", cls="alert alert-error") if error else ""

    opts_c = [Option(f"{c['nombre']} ({c['dni']})", value=str(c["id_cliente"])) for c in clientes]
    opts_v = [Option(f"#{v['id_vehiculo']} — {v.get('marca','')} {v.get('modelo','')} ({v.get('placa','')})", value=str(v["id_vehiculo"])) for v in vehiculos]

    # Formulario dinámico multilínea en JavaScript
    js_script = Script("""
        let items = [];

        function renderItems() {
            const tbody = document.getElementById('items-tbody');
            tbody.innerHTML = '';
            let total = 0;
            
            if (items.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" class="no-data" style="text-align:center; padding:1.5rem; color:var(--text-muted);">No se han agregado servicios o repuestos a la cotización.</td></tr>';
            } else {
                items.forEach((item, index) => {
                    total += item.precio;
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td style="font-weight:500;">${item.item}</td>
                        <td style="font-weight:600; color:var(--text-primary);">S/. ${item.precio.toFixed(2)}</td>
                        <td style="text-align:center;">
                            <button type="button" class="btn btn-sm btn-danger" onclick="removeItem(${index})" style="padding:0.3rem 0.6rem; font-size:0.75rem;">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            }
            
            document.getElementById('items_json').value = JSON.stringify(items);
            document.getElementById('total').value = total;
            document.getElementById('total-display').innerText = 'S/. ' + total.toFixed(2);
        }

        function addItem() {
            const itemInput = document.getElementById('item_input');
            const precioInput = document.getElementById('precio_input');
            const itemValue = itemInput.value.trim();
            const precioValue = parseFloat(precioInput.value);
            
            if (!itemValue) {
                alert('Por favor, ingresa una descripción para el ítem.');
                itemInput.focus();
                return;
            }
            if (isNaN(precioValue) || precioValue < 0) {
                alert('Por favor, ingresa un precio unitario válido mayor o igual a 0.');
                precioInput.focus();
                return;
            }
            
            items.push({ item: itemValue, precio: precioValue });
            itemInput.value = '';
            precioInput.value = '';
            renderItems();
            itemInput.focus();
        }

        function removeItem(index) {
            items.splice(index, 1);
            renderItems();
        }

        function validarFormulario(event) {
            if (items.length === 0) {
                alert('Debes agregar al menos un servicio o repuesto para poder generar la cotización.');
                event.preventDefault();
                return false;
            }
            return true;
        }

        window.addEventListener('DOMContentLoaded', () => {
            renderItems();
            
            document.getElementById('precio_input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    addItem();
                }
            });
            document.getElementById('item_input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    addItem();
                }
            });
        });
    """)

    form = Form(
        alert,
        js_script,
        Div(
            Div(Label("Cliente"), Select(Option("-- Seleccionar Cliente --", value=""), *opts_c, name="id_cliente", required=True), cls="form-group"),
            Div(Label("Vehículo"), Select(Option("-- Seleccionar Vehículo --", value=""), *opts_v, name="id_vehiculo", required=True), cls="form-group"),
            Div(Label("Fecha de Validez"), Input(name="fecha_validez", type="date", required=True), cls="form-group"),
            cls="form-grid"
        ),
        H3("Servicios y Repuestos de la Cotización", style="font-size:1rem; margin-top:1.5rem; margin-bottom:0.5rem; border-top:1px solid var(--border); padding-top:1.5rem;"),
        Div(
            Div(Label("Descripción del Servicio o Repuesto"), Input(id="item_input", placeholder="Ej: Cambio de Aceite Sintético"), cls="form-group"),
            Div(Label("Precio Unitario (S/.)"), Input(id="precio_input", type="number", min="0", step="0.01", placeholder="0.00"), cls="form-group"),
            Div(Label(style="visibility:hidden;"), Button(I(cls="fa-solid fa-plus"), " Agregar", type="button", onclick="addItem()", cls="btn btn-primary", style="margin-top:auto;"), cls="form-group"),
            cls="form-grid",
            style="margin-bottom:1rem; align-items:flex-end;"
        ),
        Div(
            Table(
                Thead(Tr(Th("Descripción del Servicio/Repuesto"), Th("Precio (S/.)"), Th("Acción", style="width:100px; text-align:center;"))),
                Tbody(id="items-tbody"),
            ),
            cls="table-wrap",
            style="margin-bottom:1rem; border:1px solid var(--border); border-radius:var(--radius); padding:0.5rem;"
        ),
        Div(
            Span("Total Cotizado:", cls="text-muted", style="font-weight:600;"),
            Span("S/. 0.00", id="total-display", style="font-size:1.3rem; font-weight:800; color:var(--accent); margin-left:0.5rem;"),
            style="text-align:right; margin-bottom:1.5rem; padding:0.5rem; background:var(--bg-page); border-radius:var(--radius); display:flex; justify-content:flex-end; align-items:center;"
        ),
        Input(type="hidden", name="items_json", id="items_json", value="[]"),
        Input(type="hidden", name="total", id="total", value="0"),
        Div(
            A("Cancelar", href="/cotizaciones", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-plus"), " Generar Cotización", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/cotizaciones/crear", onsubmit="return validarFormulario(event)"
    )

    contenido = Div(
        Div(
            Div(H2("Nueva Cotización"), A(I(cls="fa-solid fa-arrow-left"), " Volver", href="/cotizaciones", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nueva Cotización", "Nueva Cotización", "", contenido)


def render_cotizaciones_detalle(req, cotizacion):
    """
    Renderiza la vista detallada de una cotización individual.
    """
    if not cotizacion:
        return RedirectResponse("/cotizaciones", status_code=303)

    servicios = cotizacion.get("servicios_repuestos", [])
    # Corregir para usar 'item' en lugar del erróneo 'descripcion'
    filas_items = [
        Tr(
            Td(s.get("item", "—"), style="font-weight:500;"), 
            Td(f"S/. {float(s.get('precio', 0)):.2f}", style="font-weight:600; color:var(--text-primary); white-space:nowrap;")
        )
        for s in servicios
    ]

    contenido = Div(
        Div(
            Div(
                Div(
                    H2(I(cls="fa-solid fa-file-invoice-dollar"), f" Cotización {cotizacion.get('codigoCotizacion')}"),
                    Span("MongoDB", cls="db-tag mongo"),
                ),
                A(I(cls="fa-solid fa-arrow-left"), " Volver", href="/cotizaciones", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(
                Div(
                    Div(Label("Cliente"), Div(cotizacion.get("cliente_str", "—"), cls="detail-value"), cls="detail-item"),
                    Div(Label("Vehículo"), Div(cotizacion.get("vehiculo_str", "—"), cls="detail-value"), cls="detail-item"),
                    Div(Label("Válida Hasta"), Div(cotizacion.get("fecha_validez_str", "—"), cls="detail-value"), cls="detail-item"),
                    cls="detail-grid"
                ),
                Div(style="margin-top:1.5rem;"),
                H3("Detalle de Ítems", style="font-size:1rem; margin-bottom:0.5rem; border-top:1px solid var(--border); padding-top:1rem;"),
                Table(
                    Thead(Tr(Th("Descripción del Servicio/Repuesto"), Th("Precio"))),
                    Tbody(*filas_items) if filas_items else Tbody(Tr(Td("Sin ítems.", colspan="2", cls="no-data"))),
                    cls="table-wrap"
                ),
                Div(
                    Span("Total General:", cls="text-muted", style="font-weight: 600;"),
                    Span(f"S/. {cotizacion.get('total', 0):.2f}", style="font-size:1.3rem;font-weight:800;color:var(--accent); margin-left:0.5rem; white-space:nowrap;"),
                    style="margin-top:1.5rem; text-align:right; padding:0.5rem; background:var(--bg-page); border-radius:var(--radius); display:flex; justify-content:flex-end; align-items:center;"
                ),
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, f"Cotización {cotizacion.get('codigoCotizacion')}", "Detalle de Cotización", "", contenido)


