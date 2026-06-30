"""
routes/cotizaciones.py
======================
Vista para Cotizaciones.
"""
import json
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout, badge_estado
from datetime import date

hoy = date.today().strftime("%Y-%m-%d")
# ── Catálogo fijo de servicios de taller (mano de obra) ────────────────
# Vive en código, no en base de datos: son precios estándar del taller,
# no inventario físico. Se puede editar libremente aquí.
SERVICIOS_TALLER = {
    "Cambio de Aceite y Filtro":            80.00,
    "Mantenimiento Menor (10,000 km)":      150.00,
    "Mantenimiento Mayor (40,000 km)":      450.00,
    "Alineamiento y Balanceo":              90.00,
    "Cambio de Pastillas de Freno":         60.00,
    "Cambio de Discos de Freno":            120.00,
    "Purga de Sistema de Frenos":           70.00,
    "Cambio de Correa de Distribución":     250.00,
    "Cambio de Batería (Mano de Obra)":     30.00,
    "Diagnóstico Computarizado (Escáner)":  50.00,
    "Cambio de Bujías":                     45.00,
    "Cambio de Filtro de Aire":             25.00,
    "Cambio de Filtro de Combustible":      40.00,
    "Revisión y Recarga de Aire Acondicionado": 110.00,
    "Cambio de Amortiguadores (par)":       180.00,
    "Cambio de Líquido de Transmisión":     130.00,
    "Reparación de Sistema de Embrague":    320.00,
    "Cambio de Llantas (mano de obra, 4)":  60.00,
    "Lavado y Encerado General":            45.00,
    "Revisión Pre-Técnica (Checklist 30 puntos)": 35.00,
}

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
        "Presupuestos y precios comerciales",
        contenido
    )

def render_cotizaciones_nueva(req, clientes, vehiculos, repuestos=None, bitacoras=None):
    """
    Renderiza la vista del formulario dinámico de nueva cotización.
    Cascada Cliente -> Vehículo -> Diagnósticos, todo resuelto vía JS sin recargar
    (los datos completos se mandan una sola vez al navegador).
    """
    error = req.query_params.get("error", "")
    alert = Div(I(cls="fa-solid fa-circle-exclamation"), f" {error}", cls="alert alert-error") if error else ""

    repuestos = repuestos or []
    bitacoras = bitacoras or []

    opts_c = [Option(f"{c['nombre']} ({c['dni']})", value=str(c["id_cliente"])) for c in clientes]

    # Mapa idCliente -> lista de vehículos de ese cliente (para la cascada en JS)
    vehiculos_por_cliente = {}
    for v in vehiculos:
        vehiculos_por_cliente.setdefault(str(v["id_cliente"]), []).append({
            "id_vehiculo": v["id_vehiculo"],
            "label": f"#{v['id_vehiculo']} — {v.get('marca','')} {v.get('modelo','')} ({v.get('placa','')})"
        })

    # Mapa idVehiculo -> lista de bitácoras de diagnóstico de ese vehículo
    bitacoras_por_vehiculo = {}
    for b in bitacoras:
        bitacoras_por_vehiculo.setdefault(str(b.get("idVehiculo","")), []).append({
            "codigoDiagnostico": b.get("codigoDiagnostico","—"),
            "codigoEspecificacion": b.get("codigoEspecificacion","—"),
            "sintomas": b.get("sintomas", []),
            "codigo_OBD": b.get("codigo_OBD", []),
            "observaciones": b.get("observaciones", "—"),
        })

    # Mapa de repuestos del inventario: id_pieza -> {nombre, precio}
    repuestos_dict = {
        str(r["id_pieza"]): {"nombre": r["nombre"], "precio": r["precio_venta"], "stock": r["stock"]}
        for r in repuestos
    }
    opts_r = [Option(f"{r['nombre']} (Stock: {r['stock']})", value=str(r["id_pieza"])) for r in repuestos]

    opts_s = [Option(nombre, value=nombre) for nombre in SERVICIOS_TALLER.keys()]

    js_script = Script(f"""
        const serviciosData   = {json.dumps(SERVICIOS_TALLER)};
        const repuestosData   = {json.dumps(repuestos_dict)};
        const vehiculosPorCliente = {json.dumps(vehiculos_por_cliente)};
        const bitacorasPorVehiculo = {json.dumps(bitacoras_por_vehiculo)};

        let items = [];

        // ── Cascada Cliente -> Vehículo ─────────────────────────────
        function onClienteChange(idCliente) {{
            const selVeh = document.getElementById('select-vehiculo');
            const panelDiag = document.getElementById('panel-diagnosticos');
            selVeh.innerHTML = '';
            panelDiag.innerHTML = '';

            const lista = vehiculosPorCliente[idCliente] || [];
            if (lista.length === 0) {{
                selVeh.appendChild(new Option('-- Este cliente no tiene vehículos --', ''));
                return;
            }}
            selVeh.appendChild(new Option('-- Seleccionar Vehículo --', ''));
            lista.forEach(v => {{
                selVeh.appendChild(new Option(v.label, v.id_vehiculo));
            }});
        }}

        // ── Panel de Diagnósticos al elegir Vehículo ────────────────
        function onVehiculoChange(idVehiculo) {{
            const panelDiag = document.getElementById('panel-diagnosticos');
            const lista = bitacorasPorVehiculo[idVehiculo] || [];

            if (!idVehiculo) {{
                panelDiag.innerHTML = '';
                return;
            }}
            if (lista.length === 0) {{
                panelDiag.innerHTML = '<div class="alert alert-info"><i class="fa-solid fa-circle-info"></i> Este vehículo no tiene diagnósticos registrados en bitácora.</div>';
                return;
            }}

            let html = '<div class="diagnosticos-panel"><div class="diagnosticos-panel-header"><i class="fa-solid fa-stethoscope"></i> Diagnósticos registrados (' + lista.length + ')</div>';
            lista.forEach(b => {{
                const sintomasHtml = (b.sintomas || []).map(s => '<span class="tag">' + s + '</span>').join('');
                const obdHtml = (b.codigo_OBD || []).map(c => '<span class="tag-obd">' + c + '</span>').join('');
                html += '<div class="diagnostico-item">' +
                    '<div class="diagnostico-item-header">' +
                        '<span class="badge badge-gray font-mono">' + b.codigoDiagnostico + '</span>' +
                        '<span class="badge badge-blue font-mono">' + b.codigoEspecificacion + '</span>' +
                    '</div>' +
                    '<div class="diagnostico-field">' +
                        '<span class="diagnostico-field-label">Síntomas</span>' +
                        '<div class="tag-list mt-1">' + (sintomasHtml || '<span class="text-muted text-sm">Sin síntomas registrados.</span>') + '</div>' +
                    '</div>' +
                    '<div class="diagnostico-field">' +
                        '<span class="diagnostico-field-label">Códigos OBD</span>' +
                        '<div class="tag-list mt-1">' + (obdHtml || '<span class="text-muted text-sm">Sin códigos OBD.</span>') + '</div>' +
                    '</div>' +
                    '<div class="diagnostico-field">' +
                        '<span class="diagnostico-field-label">Observaciones</span>' +
                        '<p class="diagnostico-obs">' + (b.observaciones || '—') + '</p>' +
                    '</div>' +
                '</div>';
            }});
            html += '</div>';
            panelDiag.innerHTML = html;
        }}

        // ── Autocompletar precio de Servicio ────────────────────────
        function onServicioChange(nombre) {{
            const precioInput = document.getElementById('servicio_precio');
            precioInput.value = nombre ? serviciosData[nombre].toFixed(2) : '';
        }}

        function addServicio() {{
            const sel = document.getElementById('servicio_select');
            const nombre = sel.value;
            if (!nombre) {{
                alert('Selecciona un servicio.');
                return;
            }}
            items.push({{ item: nombre, precio: serviciosData[nombre] }});
            sel.value = '';
            document.getElementById('servicio_precio').value = '';
            renderItems();
        }}

        // ── Autocompletar precio de Repuesto (desde Oracle) ─────────
        function onRepuestoChange(idPieza) {{
            const precioInput = document.getElementById('repuesto_precio_unit');
            precioInput.value = idPieza ? repuestosData[idPieza].precio.toFixed(2) : '';
        }}

        function addRepuesto() {{
            const sel = document.getElementById('repuesto_select');
            const idPieza = sel.value;
            const cantidad = parseInt(document.getElementById('repuesto_cantidad').value, 10);

            if (!idPieza) {{
                alert('Selecciona un repuesto.');
                return;
            }}
            if (!cantidad || cantidad < 1) {{
                alert('Ingresa una cantidad válida (mínimo 1).');
                return;
            }}
            const rep = repuestosData[idPieza];
            if (cantidad > rep.stock) {{
                alert('Stock insuficiente. Disponible: ' + rep.stock + ', solicitado: ' + cantidad + '.');
                return;
            }}
            const costoTotal = rep.precio * cantidad;
            items.push({{ item: rep.nombre, precio: costoTotal }});

            sel.value = '';
            document.getElementById('repuesto_precio_unit').value = '';
            document.getElementById('repuesto_cantidad').value = '1';
            renderItems();
        }}

        // ── Tabla de ítems agregados (servicios + repuestos juntos) ─
        function renderItems() {{
            const tbody = document.getElementById('items-tbody');
            tbody.innerHTML = '';
            let total = 0;

            if (items.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="3" class="no-data" style="text-align:center; padding:1.5rem; color:var(--text-muted);">No se han agregado servicios o repuestos a la cotización.</td></tr>';
            }} else {{
                items.forEach((item, index) => {{
                    total += item.precio;
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td style="font-weight:500;">${{item.item}}</td>
                        <td style="font-weight:600; color:var(--text-primary);">S/. ${{item.precio.toFixed(2)}}</td>
                        <td style="text-align:center;">
                            <button type="button" class="btn btn-sm btn-danger" onclick="removeItem(${{index}})" style="padding:0.3rem 0.6rem; font-size:0.75rem;">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                }});
            }}

            document.getElementById('items_json').value = JSON.stringify(items);
            document.getElementById('total').value = total;
            document.getElementById('total-display').innerText = 'S/. ' + total.toFixed(2);
        }}

        function removeItem(index) {{
            items.splice(index, 1);
            renderItems();
        }}

        function validarFormulario(event) {{
            if (items.length === 0) {{
                alert('Debes agregar al menos un servicio o repuesto para poder generar la cotización.');
                event.preventDefault();
                return false;
            }}
            return true;
        }}

        window.addEventListener('DOMContentLoaded', () => {{
            renderItems();
        }});
    """)
    
    form = Form(
        alert,
        Div(
            Div(Label("Cliente"),
                Select(Option("-- Seleccionar Cliente --", value=""), *opts_c, name="id_cliente",
                       id="select-cliente", required=True, onchange="onClienteChange(this.value)"),
                cls="form-group"),
            Div(Label("Vehículo"),
                Select(Option("-- Primero selecciona un cliente --", value=""), name="id_vehiculo",
                       id="select-vehiculo", required=True, onchange="onVehiculoChange(this.value)"),
                cls="form-group"),
            Div(Label("Fecha de Validez"),
                Input(name="fecha_validez", type="date", min=hoy, required=True),
                cls="form-group"),
            cls="form-grid"
        ),
        Div(id="panel-diagnosticos", style="margin-top:1rem;"),
        H3("Servicios y Repuestos de la Cotización", style="font-size:1rem; margin-top:1.5rem; margin-bottom:0.5rem; border-top:1px solid var(--border); padding-top:1.5rem;"),

        # ── Bloque: agregar Servicio (catálogo fijo de mano de obra) ──
        Div(
            Div(Label("Servicio de Taller"),
                Select(Option("-- Seleccionar Servicio --", value=""), *opts_s,
                       id="servicio_select", onchange="onServicioChange(this.value)"),
                cls="form-group"),
            Div(Label("Precio (S/.)"),
                Input(id="servicio_precio", type="number", step="0.01", readonly=True, placeholder="0.00"),
                cls="form-group"),
            Div(Label(style="visibility:hidden;"),
                Button(I(cls="fa-solid fa-plus"), " Agregar Servicio", type="button",
                       onclick="addServicio()", cls="btn btn-blue", style="margin-top:auto;"),
                cls="form-group"),
            cls="form-grid",
            style="margin-bottom:.85rem; align-items:flex-end;"
        ),

        # ── Bloque: agregar Repuesto (inventario real de Oracle) ──────
        Div(
            Div(Label("Repuesto del Inventario"),
                Select(Option("-- Seleccionar Repuesto --", value=""), *opts_r,
                       id="repuesto_select", onchange="onRepuestoChange(this.value)"),
                cls="form-group"),
            Div(Label("Precio Unitario (S/.)"),
                Input(id="repuesto_precio_unit", type="number", step="0.01", readonly=True, placeholder="0.00"),
                cls="form-group"),
            Div(Label("Cantidad"),
                Input(id="repuesto_cantidad", type="number", min="1", step="1", value="1"),
                cls="form-group"),
            Div(Label(style="visibility:hidden;"),
                Button(I(cls="fa-solid fa-plus"), " Agregar Repuesto", type="button",
                       onclick="addRepuesto()", cls="btn btn-primary", style="margin-top:auto;"),
                cls="form-group"),
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
        js_script,
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

