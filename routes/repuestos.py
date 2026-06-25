"""
routes/repuestos.py — View puro de Repuestos/Inventario
========================================================
Solo renderiza HTML. Lógica en controllers/repuestos_ctrl.py.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout, stock_badge


"""
routes/repuestos.py — View puro de Repuestos/Inventario
========================================================
Solo renderiza HTML. Lógica en controllers/repuestos_ctrl.py.
"""
import json
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout, stock_badge


def render_repuestos_list(req, usuario, repuestos, todos_repuestos, q="", filtro_stock="todos", orden="nombre_asc", page=1, total_pages=1, total_count=0):
    """
    Renderiza el inventario de repuestos con filtros avanzados, paginación numérica,
    modal de detalles y confirmación modal de eliminación segura.
    """
    # 1. Alertas de confirmación y error
    msg = req.query_params.get("msg", "")
    error = req.query_params.get("error", "")
    
    alert = ""
    if msg:
        alerts_map = {
            "creado":    Div(I(cls="fa-solid fa-circle-check"), " Repuesto registrado exitosamente.", cls="alert alert-success"),
            "editado":   Div(I(cls="fa-solid fa-circle-check"), " Repuesto actualizado exitosamente.", cls="alert alert-success"),
            "eliminado": Div(I(cls="fa-solid fa-circle-check"), " Repuesto eliminado exitosamente de base de datos.", cls="alert alert-warning"),
        }
        alert = alerts_map.get(msg, "")
    elif error:
        alert = Div(I(cls="fa-solid fa-circle-exclamation"), f" {error}", cls="alert alert-error")


    def local_stock_badge(stock: int):
        if stock <= 2:
            return Span(I(cls="fa-solid fa-triangle-exclamation"), f" {stock}", cls="badge stock-badge-critical")
        elif stock <= 5:
            return Span(I(cls="fa-solid fa-bolt"), f" {stock}", cls="badge stock-badge-low")
        return Span(I(cls="fa-solid fa-check"), f" {stock}", cls="badge stock-badge-ok")

    # 2. Alertas de Stock globales calculadas sobre el total del catálogo
    criticos = [r for r in todos_repuestos if r["stock"] <= 2]
    bajos    = [r for r in todos_repuestos if 2 < r["stock"] <= 5]

    alertas_compactas_grid = Div(
        # Tarjeta Resumen Stock Crítico
        Div(
            Div(
                I(cls="fa-solid fa-triangle-exclamation"),
                cls="alert-card-icon critical"
            ),
            Div(
                Div("STOCK CRÍTICO", cls="alert-card-title critical"),
                Div(f"{len(criticos)} repuestos afectados", cls="alert-card-desc"),
                A(
                    "Ver detalle →",
                    hx_get=f"/repuestos?detalle_alerta=critico",
                    hx_target="#alerta-modal-body",
                    onclick="abrirModalAlerta('Stock Crítico (≤2 unidades)')",
                    cls="alert-card-link"
                ),
                cls="alert-card-info"
            ),
            cls="alert-card"
        ),
        # Tarjeta Resumen Stock Bajo
        Div(
            Div(
                I(cls="fa-solid fa-bolt"),
                cls="alert-card-icon low"
            ),
            Div(
                Div("STOCK BAJO", cls="alert-card-title low"),
                Div(f"{len(bajos)} repuestos afectados", cls="alert-card-desc"),
                A(
                    "Ver detalle →",
                    hx_get=f"/repuestos?detalle_alerta=bajo",
                    hx_target="#alerta-modal-body",
                    onclick="abrirModalAlerta('Stock Bajo (≤5 unidades)')",
                    cls="alert-card-link"
                ),
                cls="alert-card-info"
            ),
            cls="alert-card"
        ),
        cls="alerts-grid"
    )

    # 3. Tarjetas estadísticas globales
    stats = Div(
        Div(Div(I(cls="fa-solid fa-boxes-stacked"), cls="stat-icon orange"), Div(Div(str(len(todos_repuestos)), cls="stat-value"), Div("Total Ítems", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div(I(cls="fa-solid fa-triangle-exclamation"), cls="stat-icon red"),    Div(Div(str(len(criticos)), cls="stat-value"), Div("Stock Crítico", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div(I(cls="fa-solid fa-bolt"), cls="stat-icon yellow"),  Div(Div(str(len(bajos)), cls="stat-value"), Div("Stock Bajo", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div(I(cls="fa-solid fa-money-bill-wave"), cls="stat-icon green"),   Div(Div(f"S/. {sum(r['precio_venta']*r['stock'] for r in todos_repuestos):,.2f}", cls="stat-value"), Div("Valor Inventario", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        cls="stats-grid"
    )


    # 4. Formulario de Búsqueda y Filtros
    estados_stock = [
        ("Todos", "todos"),
        ("Stock crítico (≤2)", "critico"),
        ("Stock bajo (≤5)", "bajo"),
        ("Stock normal (>5)", "normal")
    ]
    select_stock = [
        Option(opt_label, value=opt_val, selected=(filtro_stock == opt_val))
        for opt_label, opt_val in estados_stock
    ]

    orden_opciones = [
        ("Nombre A-Z", "nombre_asc"),
        ("Nombre Z-A", "nombre_desc"),
        ("Mayor stock", "stock_desc"),
        ("Menor stock", "stock_asc"),
        ("Mayor precio", "precio_desc"),
        ("Menor precio", "precio_asc")
    ]
    select_orden = [
        Option(opt_label, value=opt_val, selected=(orden == opt_val))
        for opt_label, opt_val in orden_opciones
    ]

    filter_form = Form(
        Div(
            Div(
                Label("Búsqueda"),
                Input(name="q", placeholder="Código, nombre, proveedor...", value=q),
                cls="form-group"
            ),
            Div(
                Label("Stock"),
                Select(*select_stock, name="filtro_stock"),
                cls="form-group"
            ),
            Div(
                Label("Ordenar por"),
                Select(*select_orden, name="orden"),
                cls="form-group"
            ),
            Div(
                Label(style="visibility:hidden;"),
                Div(
                    Button(I(cls="fa-solid fa-magnifying-glass"), " Buscar", type="submit", cls="btn btn-primary"),
                    A(I(cls="fa-solid fa-filter-circle-xmark"), " Limpiar", href="/repuestos", cls="btn btn-secondary"),
                    style="display:flex; gap:0.5rem;"
                ),
                cls="form-group"
            ),
            cls="form-grid",
            style="margin-bottom:0.5rem; align-items: flex-end;"
        ),
        method="get", action="/repuestos",
        cls="filter-card",
        style="padding:1.25rem; background:var(--bg-page); border:1.5px solid var(--border); border-radius:var(--radius); margin-bottom:1.5rem;"
    )

    # 5. Generar filas de la tabla
    filas = []
    for r in repuestos:
        acciones = [
            Button(
                I(cls="fa-solid fa-eye"), " Ver",
                onclick=f"verDetalle('{r['id_pieza']}')",
                cls="btn btn-sm btn-secondary",
                title="Ver detalle de repuesto",
                style="padding: 0.35rem 0.7rem; font-size: 0.8rem;"
            )
        ]
        if puede_acceder(usuario, "repuestos", "editar"):
            acciones.append(
                A(
                    I(cls="fa-solid fa-pen-to-square"), " Editar",
                    href=f"/repuestos/{r['id_pieza']}/editar",
                    cls="btn btn-sm btn-secondary",
                    style="padding: 0.35rem 0.7rem; font-size: 0.8rem;"
                )
            )
        if puede_acceder(usuario, "repuestos", "eliminar"):
            acciones.append(
                Button(
                    I(cls="fa-solid fa-trash"), " Eliminar",
                    onclick=f"confirmarEliminar('{r['id_pieza']}', '{r['codigo']}')",
                    cls="btn btn-sm btn-danger",
                    title="Eliminar repuesto",
                    style="padding: 0.35rem 0.7rem; font-size: 0.8rem;"
                )
            )

        filas.append(Tr(
            Td(Span(r["codigo"], cls="font-mono badge badge-gray"), data_label="Código"),
            Td(Span(r["nombre"], style="font-weight:600; color:var(--text-primary);"), data_label="Nombre"),
            Td(local_stock_badge(r["stock"]), data_label="Stock"),
            Td(f"S/. {r['precio_venta']:.2f}", style="font-weight:500;", data_label="Precio Venta"),
            Td(r["proveedor"], data_label="Proveedor"),
            Td(Div(*acciones, cls="flex gap-1") if acciones else "—", data_label="Acciones"),
        ))

    crear_btn = (
        A(
            I(cls="fa-solid fa-plus"), " Nuevo Repuesto",
            href="/repuestos/nuevo",
            cls="btn btn-primary"
        )
        if puede_acceder(usuario, "repuestos", "crear")
        else ""
    )

    tabla = Div(
        Table(
            Thead(Tr(
                Th("Código"),
                Th("Nombre"),
                Th("Stock"),
                Th("Precio Venta"),
                Th("Proveedor"),
                Th("Acciones")
            )),
            Tbody(*filas) if filas else Tbody(Tr(Td("Sin repuestos para los filtros aplicados.", colspan="6", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    # 6. Paginación deslizante (máximo 5 páginas visibles)
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
    query_str = f"&q={q}&filtro_stock={filtro_stock}&orden={orden}"
    for p in range(start_page, end_page + 1):
        is_current = (p == page)
        btn_cls = "btn btn-sm btn-primary" if is_current else "btn btn-sm btn-secondary"
        page_buttons.append(
            A(
                str(p),
                href=f"/repuestos?page={p}{query_str}",
                cls=btn_cls,
                style="min-width:32px; text-align:center;"
            )
        )

    # Paginación Anterior / Siguiente
    if page > 1:
        pag_prev = A(
            I(cls="fa-solid fa-chevron-left"), " Anterior",
            href=f"/repuestos?page={page - 1}{query_str}",
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
            href=f"/repuestos?page={page + 1}{query_str}",
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

    # 7. Modal de Vista Detallada de Repuesto
    modal_detalle = Div(
        Div(
            Div(
                H3(I(cls="fa-solid fa-box"), " Detalle de Repuesto"),
                Button("×", onclick="cerrarModalDetalle()", cls="tech-modal-close"),
                cls="tech-modal-header"
            ),
            Div(
                Div(
                    Div(Label("Código de Repuesto"), Div(id="det-modal-codigo", cls="tech-val font-mono"), cls="tech-item"),
                    Div(Label("Nombre descriptivo"), Div(id="det-modal-nombre", cls="tech-val"), cls="tech-item"),
                    Div(Label("Stock Disponible"), Div(id="det-modal-stock", cls="tech-val"), cls="tech-item"),
                    Div(Label("Precio de Venta"), Div(id="det-modal-precio", cls="tech-val"), cls="tech-item"),
                    Div(Label("Proveedor Asignado"), Div(id="det-modal-proveedor", cls="tech-val"), cls="tech-item"),
                    Div(Label("Estado de Inventario"), Div(id="det-modal-estado", style="display:flex; align-items:center;"), cls="tech-item"),
                    cls="tech-grid"
                ),
                cls="tech-modal-body"
            ),
            cls="tech-modal-content"
        ),
        id="det-modal",
        cls="tech-modal"
    )

    # 8. Modal de Confirmación de Eliminación Segura
    modal_eliminar = Div(
        Div(
            Div(
                H3(I(cls="fa-solid fa-triangle-exclamation"), " Confirmar Eliminación"),
                Button("×", onclick="cerrarModalEliminar()", cls="tech-modal-close"),
                cls="tech-modal-header"
            ),
            Div(
                P(
                    "¿Desea eliminar de forma permanente el repuesto ",
                    Span(id="del-modal-codigo", style="font-weight:700; color:var(--brand-primary);"),
                    " del catálogo de inventario?",
                    style="margin-bottom:1.5rem;"
                ),
                Form(
                    Input(type="hidden", name="id_pieza", id="del-modal-id"),
                    Div(
                        Button("Cancelar", type="button", onclick="cerrarModalEliminar()", cls="btn btn-secondary"),
                        Button(I(cls="fa-solid fa-trash"), " Eliminar", type="submit", cls="btn btn-danger"),
                        style="display:flex; justify-content:flex-end; gap:0.75rem;"
                    ),
                    method="post", action="/repuestos/eliminar"
                ),
                cls="tech-modal-body"
            ),
            cls="tech-modal-content"
        ),
        id="del-modal",
        cls="tech-modal"
    )

    # 9. Mapear datos a Javascript
    repuestos_dict = {}
    for r in repuestos:
        stock = r["stock"]
        if stock <= 2:
            estado_html = '<span class="badge stock-critical"><i class="fa-solid fa-triangle-exclamation"></i> Crítico (≤2)</span>'
        elif stock <= 5:
            estado_html = '<span class="badge stock-low"><i class="fa-solid fa-bolt"></i> Bajo (≤5)</span>'
        else:
            estado_html = '<span class="badge stock-ok"><i class="fa-solid fa-check"></i> Normal (>5)</span>'
            
        repuestos_dict[r["id_pieza"]] = {
            "codigo": r.get("codigo", "—"),
            "nombre": r.get("nombre", "—"),
            "stock": r.get("stock", 0),
            "precio": r.get("precio_venta", 0.0),
            "proveedor": r.get("proveedor", "—"),
            "estado_html": estado_html
        }

    # 10. CSS Local para Alertas y Badges de Stock Semánticos
    css_local = Style("""
        .alerts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        .alert-card {
            display: flex;
            align-items: center;
            padding: 1.25rem;
            background: var(--bg-card);
            border: 1.5px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }
        .alert-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }
        .alert-card-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            margin-right: 1rem;
            font-size: 1.25rem;
        }
        .alert-card-icon.critical {
            background-color: var(--red-bg);
            color: var(--red);
        }
        .alert-card-icon.low {
            background-color: var(--yellow-bg);
            color: var(--yellow);
        }
        .alert-card-info {
            flex-grow: 1;
        }
        .alert-card-title {
            font-weight: 700;
            font-size: 0.9rem;
            letter-spacing: 0.05em;
            margin-bottom: 0.25rem;
            text-transform: uppercase;
        }
        .alert-card-title.critical {
            color: var(--red);
        }
        .alert-card-title.low {
            color: var(--yellow);
        }
        .alert-card-desc {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }
        .alert-card-link {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--accent);
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            transition: color 0.2s ease;
        }
        .alert-card-link:hover {
            color: var(--accent-dark);
            text-decoration: underline;
        }
        
        .stock-badge-ok {
            background-color: var(--green-bg) !important;
            color: var(--green) !important;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }
        .stock-badge-low {
            background-color: var(--yellow-bg) !important;
            color: var(--yellow) !important;
            border: 1px solid rgba(245, 158, 11, 0.2);
        }
        .stock-badge-critical {
            background-color: var(--red-bg) !important;
            color: var(--red) !important;
            border: 1px solid rgba(239, 68, 68, 0.2);
        }
    """)

    modal_alerta = Div(
        Div(
            Div(
                H3(I(cls="fa-solid fa-bell"), " Detalle de Alerta", id="alerta-modal-title"),
                Button("×", onclick="cerrarModalAlerta()", cls="tech-modal-close"),
                cls="tech-modal-header"
            ),
            Div(
                id="alerta-modal-body",
                cls="tech-modal-body"
            ),
            cls="tech-modal-content"
        ),
        id="alerta-modal",
        cls="tech-modal"
    )

    js_script = Script(f"""
        const repuestosData = {json.dumps(repuestos_dict)};
        
        function verDetalle(id) {{
            const data = repuestosData[id];
            if (!data) return;
            
            document.getElementById('det-modal-codigo').innerText = data.codigo;
            document.getElementById('det-modal-nombre').innerText = data.nombre;
            document.getElementById('det-modal-stock').innerText = data.stock + " unidades";
            document.getElementById('det-modal-precio').innerText = "S/. " + data.precio.toFixed(2);
            document.getElementById('det-modal-proveedor').innerText = data.proveedor;
            document.getElementById('det-modal-estado').innerHTML = data.estado_html;
            
            document.getElementById('det-modal').classList.add('active');
        }}
        
        function cerrarModalDetalle() {{
            document.getElementById('det-modal').classList.remove('active');
        }}
        
        function abrirModalAlerta(titulo) {{
            document.getElementById('alerta-modal-title').innerHTML = '<i class="fa-solid fa-bell"></i> ' + titulo;
            document.getElementById('alerta-modal-body').innerHTML = '<div style="text-align:center;padding:2rem;"><i class="fa-solid fa-spinner fa-spin"></i> Cargando detalles...</div>';
            document.getElementById('alerta-modal').classList.add('active');
        }}
        
        function cerrarModalAlerta() {{
            document.getElementById('alerta-modal').classList.remove('active');
        }}
        
        function confirmarEliminar(id, codigo) {{
            document.getElementById('del-modal-id').value = id;
            document.getElementById('del-modal-codigo').innerText = codigo;
            document.getElementById('del-modal').classList.add('active');
        }}
        
        function cerrarModalEliminar() {{
            document.getElementById('del-modal').classList.remove('active');
        }}
        
        // Cerrar modales al hacer clic en fondo
        window.addEventListener('click', function(e) {{
            const detModal = document.getElementById('det-modal');
            const delModal = document.getElementById('del-modal');
            const alertaModal = document.getElementById('alerta-modal');
            if (e.target === detModal) {{
                cerrarModalDetalle();
            }}
            if (e.target === delModal) {{
                cerrarModalEliminar();
            }}
            if (e.target === alertaModal) {{
                cerrarModalAlerta();
            }}
        }});
    """)

    contenido = Div(
        css_local,
        alert, stats, alertas_compactas_grid,
        Div(
            Div(
                H2(I(cls="fa-solid fa-gears"), " Inventario de Repuestos"),
                Span("Oracle", cls="db-tag oracle"),
                cls="card-header"
            ),
            Div(
                Div(
                    P("Gestión de piezas de recambio y stock automotriz relacional en Oracle.", cls="text-muted text-sm"),
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
        modal_detalle,
        modal_eliminar,
        modal_alerta,
        js_script,
        cls="page-body"
    )
    return layout(req, "Repuestos", "Inventario de Repuestos", "Base de datos Oracle", contenido)



def render_repuestos_nuevo(req):
    """Renderiza el formulario de nuevo repuesto."""
    error = req.query_params.get("error", "")
    alert = Div(I(cls="fa-solid fa-circle-exclamation"), f" {error}", cls="alert alert-error") if error else ""

    form = Form(
        alert,
        Div(
            Div(Label("Código"),            Input(name="codigo",      placeholder="FIL-ACE-016", required=True), cls="form-group"),
            Div(Label("Nombre"),            Input(name="nombre",      placeholder="Filtro de Aceite...", required=True), cls="form-group"),
            Div(Label("Stock inicial"),     Input(name="stock",       type="number", min="0", value="1", required=True), cls="form-group"),
            Div(Label("Precio de venta (S/.)"), Input(name="precio_venta", type="number", step="0.01", min="0", placeholder="0.00", required=True), cls="form-group"),
            Div(Label("Proveedor"),         Input(name="proveedor",   placeholder="AutoParts SAC", required=True), cls="form-group"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/repuestos", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Guardar Repuesto", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/repuestos/crear"
    )

    contenido = Div(
        Div(
            Div(
                H2(I(cls="fa-solid fa-plus"), " Nuevo Repuesto"),
                A("← Volver", href="/repuestos", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nuevo Repuesto", "Nuevo Repuesto", "", contenido)


def render_repuestos_editar(req, repuesto):
    """Renderiza el formulario de edición de un repuesto."""
    id_pieza = repuesto["id_pieza"]
    form = Form(
        Div(
            Div(Label("Código"),        Input(name="codigo",      value=repuesto["codigo"],      required=True), cls="form-group"),
            Div(Label("Nombre"),        Input(name="nombre",      value=repuesto["nombre"],      required=True), cls="form-group"),
            Div(Label("Stock"),         Input(name="stock",       type="number", min="0", value=str(repuesto["stock"]), required=True), cls="form-group"),
            Div(Label("Precio (S/.)"),  Input(name="precio_venta",type="number", step="0.01", value=str(repuesto["precio_venta"]), required=True), cls="form-group"),
            Div(Label("Proveedor"),     Input(name="proveedor",   value=repuesto["proveedor"],   required=True), cls="form-group"),
            cls="form-grid"
        ),
        Input(type="hidden", name="id_pieza", value=str(id_pieza)),
        Div(
            A("Cancelar", href="/repuestos", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Actualizar Repuesto", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/repuestos/actualizar"
    )

    contenido = Div(
        Div(
            Div(
                H2(I(cls="fa-solid fa-pen-to-square"), f" Editar: {repuesto['nombre']}"),
                A("← Volver", href="/repuestos", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Editar Repuesto", f"Editar: {repuesto['nombre']}", "", contenido)


def render_detalle_alerta_fragment(items):
    """
    Retorna la tabla de detalles de stock crítico/bajo para ser renderizada en el modal vía HTMX.
    """
    if not items:
        return Div(P("No hay repuestos en esta categoría.", cls="text-muted"), style="padding:1.5rem; text-align:center;")
    
    filas = []
    for r in items:
        stock = r["stock"]
        if stock <= 2:
            st_badge = Span(I(cls="fa-solid fa-triangle-exclamation"), f" {stock}", cls="badge stock-badge-critical")
        elif stock <= 5:
            st_badge = Span(I(cls="fa-solid fa-bolt"), f" {stock}", cls="badge stock-badge-low")
        else:
            st_badge = Span(I(cls="fa-solid fa-check"), f" {stock}", cls="badge stock-badge-ok")
            
        filas.append(Tr(
            Td(Span(r["codigo"], cls="font-mono badge badge-gray")),
            Td(r["nombre"], style="font-weight:600; color:var(--text-primary);"),
            Td(st_badge),
            Td(r["proveedor"])
        ))
        
    return Table(
        Thead(Tr(
            Th("Código"),
            Th("Nombre"),
            Th("Stock"),
            Th("Proveedor")
        )),
        Tbody(*filas),
        cls="table-wrap"
    )

