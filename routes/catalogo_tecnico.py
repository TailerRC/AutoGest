"""
routes/catalogo_tecnico.py — View puro del Catálogo Técnico
===========================================================
Solo renderiza HTML. Lógica en controllers/catalogo_ctrl.py.
"""
import json
from fasthtml.common import *
from .helpers import layout


def render_catalogo_list(req, catalogo, codigo="", marca="", modelo="", año_s="", motor="", aceite="", page=1, total_pages=1, total_count=0):
    """
    Renderiza el catálogo de especificaciones técnicas en una tabla moderna,
    interactiva, compatible con pantallas móviles y con modal de ficha técnica.
    """
    
    # 1. Panel de Búsqueda y Filtros Avanzados
    busqueda = Form(
        Div(
            Div(Label("Código"), Input(name="codigo", value=codigo, placeholder="COD-..."), cls="form-group"),
            Div(Label("Marca"),  Input(name="marca",  value=marca,  placeholder="Toyota, Kia..."), cls="form-group"),
            Div(Label("Modelo"), Input(name="modelo", value=modelo, placeholder="Corolla, Rio..."), cls="form-group"),
            Div(Label("Año"),    Input(name="año",    type="number", value=año_s, placeholder="2020", min="1990", max="2030"), cls="form-group"),
            Div(Label("Motor"),  Input(name="motor",  value=motor,  placeholder="2.0L, 1.6 VVT..."), cls="form-group"),
            Div(Label("Aceite"),  Input(name="aceite", value=aceite, placeholder="5W-30, 10W-40..."), cls="form-group"),
            cls="form-grid"
        ),
        Div(
            Button(I(cls="fa-solid fa-magnifying-glass"), " Buscar", type="submit", cls="btn btn-primary"),
            A(I(cls="fa-solid fa-filter-circle-xmark"), " Limpiar", href="/catalogo", cls="btn btn-secondary"),
            cls="form-actions",
            style="margin-top:1rem; border-top:none; padding-top:0;"
        ),
        method="get", action="/catalogo",
        cls="filter-card",
        style="padding:1.25rem; background:var(--bg-page); border:1.5px solid var(--border); border-radius:var(--radius); margin-bottom:1.5rem;"
    )

    # 2. Construcción de filas de la tabla
    filas = []
    for esp in catalogo:
        det_tec = esp.get("detalles_tecnicos", {})
        codigo_val = esp.get("codigoEspecificacion", "—")
        
        acciones = [
            # Ver especificación
            Button(
                I(cls="fa-solid fa-eye"), " Ver",
                onclick=f"verDetalle('{codigo_val}')",
                cls="btn btn-sm btn-secondary",
                title="Ver especificación",
                style="padding: 0.35rem 0.7rem; font-size: 0.8rem;"
            ),
            # Editar especificación
            A(
                I(cls="fa-solid fa-pen"), " Editar",
                href="#",
                onclick="alert('La edición de fichas del catálogo técnico está reservada para administradores del sistema.'); return false;",
                cls="btn btn-sm btn-secondary",
                title="Editar especificación",
                style="padding: 0.35rem 0.7rem; font-size: 0.8rem;"
            )
        ]

        filas.append(Tr(
            Td(
                Span(codigo_val, cls="font-mono badge badge-gray"),
                data_label="Código"
            ),
            Td(
                Span(esp.get("marca", "—"), style="font-weight:600; color:var(--text-primary);"),
                data_label="Marca"
            ),
            Td(
                Span(esp.get("modelo", "—"), style="font-weight:500;"),
                data_label="Modelo"
            ),
            Td(
                Span(str(esp.get("anio", "—")), cls="badge badge-gray"),
                data_label="Año"
            ),
            Td(
                Span(det_tec.get("motor", "—")),
                data_label="Motor"
            ),
            Td(
                Span(det_tec.get("aceite", "—"), style="font-style:italic; font-weight:500; color:var(--brand-secondary-dark);"),
                data_label="Aceite"
            ),
            Td(
                Div(*acciones, cls="flex gap-1"),
                data_label="Acciones"
            )
        ))

    tabla = Div(
        Table(
            Thead(Tr(
                Th("Código"),
                Th("Marca"),
                Th("Modelo"),
                Th("Año"),
                Th("Motor"),
                Th("Aceite"),
                Th("Acciones")
            )),
            Tbody(*filas) if filas else Tbody(Tr(Td("No se encontraron especificaciones con los filtros aplicados.", colspan="7", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    # 3. Paginación deslizante (máximo 5 páginas visibles)
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
    query_str = f"&codigo={codigo}&marca={marca}&modelo={modelo}&año={año_s}&motor={motor}&aceite={aceite}"
    for p in range(start_page, end_page + 1):
        is_current = (p == page)
        btn_cls = "btn btn-sm btn-primary" if is_current else "btn btn-sm btn-secondary"
        page_buttons.append(
            A(
                str(p),
                href=f"/catalogo?page={p}{query_str}",
                cls=btn_cls,
                style="min-width:32px; text-align:center;"
            )
        )

    # Paginación Anterior / Siguiente
    if page > 1:
        pag_prev = A(
            I(cls="fa-solid fa-chevron-left"), " Anterior",
            href=f"/catalogo?page={page - 1}{query_str}",
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
            href=f"/catalogo?page={page + 1}{query_str}",
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

    # 4. Modal para Ficha Técnica Detallada
    modal = Div(
        Div(
            Div(
                H3(I(cls="fa-solid fa-file-invoice"), " Ficha Técnica de Vehículo"),
                Button("×", onclick="cerrarModal()", cls="tech-modal-close"),
                cls="tech-modal-header"
            ),
            Div(
                Div(
                    Div(Label("Código de Especificación"), Div(id="modal-codigo", cls="tech-val font-mono"), cls="tech-item"),
                    Div(Label("Marca"), Div(id="modal-marca", cls="tech-val"), cls="tech-item"),
                    Div(Label("Modelo"), Div(id="modal-modelo", cls="tech-val"), cls="tech-item"),
                    Div(Label("Año de Fabricación"), Div(id="modal-anio", cls="tech-val"), cls="tech-item"),
                    Div(Label("Motorización"), Div(id="modal-motor", cls="tech-val"), cls="tech-item"),
                    Div(Label("Aceite Recomendado"), Div(id="modal-aceite", cls="tech-val"), cls="tech-item"),
                    Div(Label("Transmisión"), Div(id="modal-transmision", cls="tech-val"), cls="tech-item"),
                    Div(Label("Bujías"), Div(id="modal-bujias", cls="tech-val"), cls="tech-item"),
                    Div(Label("Batería"), Div(id="modal-bateria", cls="tech-val"), cls="tech-item"),
                    Div(
                        Label("Detalles Adicionales"), 
                        Div(id="modal-otros", cls="tech-val"), 
                        cls="tech-item", 
                        id="modal-otros-group", 
                        style="grid-column: 1 / -1; display:none;"
                    ),
                    cls="tech-grid"
                ),
                cls="tech-modal-body"
            ),
            cls="tech-modal-content"
        ),
        id="tech-modal",
        cls="tech-modal"
    )

    # 5. Serializar catálogo completo para consulta JS del modal
    catalogo_dict = {}
    for esp in catalogo:
        det_tec = esp.get("detalles_tecnicos", {})
        codigo_val = esp.get("codigoEspecificacion", "—")
        catalogo_dict[codigo_val] = {
            "codigo": codigo_val,
            "marca": esp.get("marca", "—"),
            "modelo": esp.get("modelo", "—"),
            "anio": esp.get("anio", "—"),
            "motor": det_tec.get("motor", "—"),
            "aceite": det_tec.get("aceite", "—"),
            "transmision": det_tec.get("transmision", "—"),
            "bujias": det_tec.get("bujias", "—"),
            "bateria": det_tec.get("batería", "—") or det_tec.get("bateria", "—"),
            "otros": det_tec.get("otros", "—")
        }

    js_script = Script(f"""
        const specsData = {json.dumps(catalogo_dict)};
        
        function verDetalle(codigo) {{
            const data = specsData[codigo];
            if (!data) return;
            
            document.getElementById('modal-codigo').innerText = data.codigo;
            document.getElementById('modal-marca').innerText = data.marca;
            document.getElementById('modal-modelo').innerText = data.modelo;
            document.getElementById('modal-anio').innerText = data.anio;
            document.getElementById('modal-motor').innerText = data.motor;
            document.getElementById('modal-aceite').innerText = data.aceite;
            document.getElementById('modal-transmision').innerText = data.transmision;
            document.getElementById('modal-bujias').innerText = data.bujias;
            document.getElementById('modal-bateria').innerText = data.bateria;
            
            const otrosVal = document.getElementById('modal-otros');
            const otrosGroup = document.getElementById('modal-otros-group');
            if (data.otros && data.otros !== '—' && data.otros !== '') {{
                otrosVal.innerText = data.otros;
                otrosGroup.style.display = 'block';
            }} else {{
                otrosGroup.style.display = 'none';
            }}
            
            document.getElementById('tech-modal').classList.add('active');
        }}
        
        function cerrarModal() {{
            document.getElementById('tech-modal').classList.remove('active');
        }}
        
        // Cerrar modal al hacer clic en fondo
        window.addEventListener('click', function(e) {{
            const modal = document.getElementById('tech-modal');
            if (e.target === modal) {{
                cerrarModal();
            }}
        }});
    """)

    # 6. Estructura de contenido final
    contenido = Div(
        Div(
            Div(
                H2(I(cls="fa-solid fa-book"), " Catálogo Técnico"),
                Span("MongoDB", cls="db-tag mongo"),
                cls="card-header"
            ),
            Div(
                P("Directorio de especificaciones y fichas técnicas vehiculares en base de datos NoSQL.", cls="text-muted text-sm"),
                style="margin-bottom:1.5rem;"
            ),
            cls="card mb-2"
        ),
        busqueda,
        Div(
            Div(
                tabla,
                paginacion,
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        modal,
        js_script,
        cls="page-body"
    )

    return layout(req, "Catálogo Técnico", "Catálogo de Especificaciones", "Base de datos MongoDB", contenido)

