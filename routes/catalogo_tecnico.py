"""
routes/catalogo_tecnico.py — View puro del Catálogo Técnico
===========================================================
Solo renderiza HTML. Lógica en controllers/catalogo_ctrl.py.
"""
import json
from fasthtml.common import *
from .helpers import layout
from auth import puede_acceder

def render_catalogo_list(req, catalogo, usuario, codigo="", marca="", modelo="", año_s="", motor="", aceite="", page=1, total_pages=1, total_count=0):
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
            Button(
                I(cls="fa-solid fa-eye"),
                onclick=f"abrirModal('{codigo_val}', false)",
                cls="btn-icon icon-view",
                type="button",
                **{"data-tooltip": "Ver especificación"}
            )
        ]
        if puede_acceder(usuario, "catalogo", "editar"):
            acciones.append(
                Button(
                    I(cls="fa-solid fa-pen"),
                    onclick=f"abrirModal('{codigo_val}', true)",
                    cls="btn-icon icon-edit",
                    type="button",
                    **{"data-tooltip": "Editar especificación"}
                )
            )

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
                Div(*acciones, cls="row-actions"),
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
    msg = req.query_params.get("msg", "")
    error = req.query_params.get("error", "")
    alert_top = ""
    if msg == "editado":
        alert_top = Div(
            Div(I(cls="fa-solid fa-circle-check"), " Especificación actualizada correctamente.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        )
    elif error:
        alert_top = Div(
            Div(I(cls="fa-solid fa-circle-exclamation"), f" {error}", cls="alert-message"),
            cls="alert alert-error"
        )

    modal_estilos = Style("""
        .tech-modal-content { max-width: 640px; }
        .tech-modal-header {
            background: linear-gradient(135deg, var(--brand-primary), var(--brand-primary-dark, #5a0a0d));
            color: #fff;
            border-radius: 12px 12px 0 0;
            padding: 1.25rem 1.5rem;
        }
        .tech-modal-header h3 { color: #fff; margin: 0; }
        .tech-modal-header .tech-modal-close { color: #fff; opacity: .8; }
        .tech-modal-header .tech-modal-close:hover { opacity: 1; }

        .tech-section-title {
            font-size: .72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .06em;
            color: var(--brand-secondary);
            margin: 1.25rem 0 .6rem;
            padding-bottom: .4rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: .4rem;
        }
        .tech-section-title:first-of-type { margin-top: 0; }

        .tech-field {
            display: flex;
            flex-direction: column;
            gap: .3rem;
        }
        .tech-field label {
            font-size: .72rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: .04em;
            display: flex;
            align-items: center;
            gap: .35rem;
        }
        .tech-field label i { color: var(--brand-secondary); font-size: .8rem; }

        .tech-val-display {
            font-size: .95rem;
            font-weight: 600;
            color: var(--text-primary);
            padding: .5rem .65rem;
            background: var(--brand-secondary-light);
            border-radius: 8px;
            border: 1px solid var(--border);
        }

        .tech-input {
            font-size: .9rem;
            padding: .55rem .7rem;
            border: 1.5px solid var(--border);
            border-radius: 8px;
            background: #fff;
            color: var(--text-primary);
            transition: border-color .15s, box-shadow .15s;
            width: 100%;
            box-sizing: border-box;
        }
        .tech-input:focus {
            outline: none;
            border-color: var(--brand-primary);
            box-shadow: 0 0 0 3px var(--brand-primary-light);
        }

        .tech-grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: .9rem;
        }
        @media (max-width: 600px) {
            .tech-grid-2 { grid-template-columns: 1fr; }
        }
    """)

    modal = Div(
        Div(
            Div(
                H3(I(cls="fa-solid fa-file-invoice"), " Ficha Técnica de Vehículo", id="modal-titulo"),
                Button("×", onclick="cerrarModal()", cls="tech-modal-close", type="button"),
                cls="tech-modal-header"
            ),
            Form(
                Div(
                    Div(I(cls="fa-solid fa-car-side"), " Datos generales", cls="tech-section-title"),
                    Div(
                        Div(
                            Label(I(cls="fa-solid fa-hashtag"), " Código de especificación"),
                            Div(id="modal-codigo", cls="tech-val-display font-mono"),
                            cls="tech-field"
                        ),
                        Div(
                            Label(I(cls="fa-solid fa-tag"), " Marca"),
                            Div(id="modal-marca-view", cls="tech-val-display"),
                            Input(id="modal-marca-edit", name="marca", cls="tech-input", style="display:none;"),
                            cls="tech-field"
                        ),
                        Div(
                            Label(I(cls="fa-solid fa-car"), " Modelo"),
                            Div(id="modal-modelo-view", cls="tech-val-display"),
                            Input(id="modal-modelo-edit", name="modelo", cls="tech-input", style="display:none;"),
                            cls="tech-field"
                        ),
                        Div(
                            Label(I(cls="fa-solid fa-calendar"), " Año de fabricación"),
                            Div(id="modal-anio-view", cls="tech-val-display"),
                            Input(id="modal-anio-edit", name="anio", type="number", cls="tech-input", style="display:none;"),
                            cls="tech-field"
                        ),
                        cls="tech-grid-2"
                    ),

                    Div(I(cls="fa-solid fa-gears"), " Especificaciones técnicas", cls="tech-section-title"),
                    Div(
                        Div(
                            Label(I(cls="fa-solid fa-engine"), " Motorización"),
                            Div(id="modal-motor-view", cls="tech-val-display"),
                            Input(id="modal-motor-edit", name="motor", cls="tech-input", style="display:none;"),
                            cls="tech-field"
                        ),
                        Div(
                            Label(I(cls="fa-solid fa-oil-can"), " Aceite recomendado"),
                            Div(id="modal-aceite-view", cls="tech-val-display"),
                            Input(id="modal-aceite-edit", name="aceite", cls="tech-input", style="display:none;"),
                            cls="tech-field"
                        ),
                        Div(
                            Label(I(cls="fa-solid fa-gear"), " Transmisión"),
                            Div(id="modal-transmision-view", cls="tech-val-display"),
                            Input(id="modal-transmision-edit", name="transmision", cls="tech-input", style="display:none;"),
                            cls="tech-field"
                        ),
                        Div(
                            Label(I(cls="fa-solid fa-bolt"), " Bujías"),
                            Div(id="modal-bujias-view", cls="tech-val-display"),
                            Input(id="modal-bujias-edit", name="bujias", cls="tech-input", style="display:none;"),
                            cls="tech-field"
                        ),
                        Div(
                            Label(I(cls="fa-solid fa-car-battery"), " Batería"),
                            Div(id="modal-bateria-view", cls="tech-val-display"),
                            Input(id="modal-bateria-edit", name="bateria", cls="tech-input", style="display:none;"),
                            cls="tech-field"
                        ),
                        cls="tech-grid-2"
                    ),

                    Div(
                        Label(I(cls="fa-solid fa-circle-info"), " Detalles adicionales"),
                        Div(id="modal-otros-view", cls="tech-val-display"),
                        Input(id="modal-otros-edit", name="otros", cls="tech-input", style="display:none;"),
                        cls="tech-field",
                        id="modal-otros-group",
                        style="margin-top:.9rem;display:none;"
                    ),
                    cls="tech-modal-body",
                    style="padding:1.25rem 1.5rem;"
                ),
                Input(type="hidden", name="codigo", id="modal-codigo-hidden"),
                Div(
                    Button("Cancelar", type="button", cls="btn btn-secondary", onclick="cerrarModal()"),
                    Button(I(cls="fa-solid fa-floppy-disk"), " Guardar cambios",
                        type="submit", id="modal-btn-guardar", cls="btn btn-primary",
                        style="display:none;"),
                    cls="form-actions",
                    style="padding:0 1.5rem 1.25rem;"
                ),
                method="post", action="/catalogo/actualizar",
                id="modal-form"
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
        let modoEdicion = false;

        function abrirModal(codigo, editar) {{
            const data = specsData[codigo];
            if (!data) return;
            modoEdicion = editar;

            document.getElementById('modal-titulo').innerHTML =
                (editar ? '<i class="fa-solid fa-pen"></i> Editar Ficha Técnica' : '<i class="fa-solid fa-file-invoice"></i> Ficha Técnica de Vehículo');
            document.getElementById('modal-btn-guardar').style.display = editar ? 'inline-flex' : 'none';
            document.getElementById('modal-codigo-hidden').value = data.codigo;
            document.getElementById('modal-codigo').innerText = data.codigo;

            const campos = ['marca','modelo','anio','motor','aceite','transmision','bujias','bateria'];
            campos.forEach(function(c) {{
                const viewEl = document.getElementById('modal-' + c + '-view');
                const editEl = document.getElementById('modal-' + c + '-edit');
                const val = data[c] === '—' ? '' : data[c];
                viewEl.innerText = data[c];
                editEl.value = val;
                viewEl.style.display = editar ? 'none' : 'block';
                editEl.style.display = editar ? 'block' : 'none';
            }});

            const otrosGroup = document.getElementById('modal-otros-group');
            const otrosView = document.getElementById('modal-otros-view');
            const otrosEdit = document.getElementById('modal-otros-edit');
            const otrosVal = (data.otros === '—') ? '' : data.otros;
            otrosEdit.value = otrosVal;
            if (editar) {{
                otrosGroup.style.display = 'block';
                otrosView.style.display = 'none';
                otrosEdit.style.display = 'block';
            }} else if (otrosVal) {{
                otrosGroup.style.display = 'block';
                otrosView.style.display = 'block';
                otrosEdit.style.display = 'none';
                otrosView.innerText = data.otros;
            }} else {{
                otrosGroup.style.display = 'none';
            }}

            document.getElementById('tech-modal').classList.add('active');
        }}

        function cerrarModal() {{
            document.getElementById('tech-modal').classList.remove('active');
        }}

        window.addEventListener('click', function(e) {{
            const modal = document.getElementById('tech-modal');
            if (e.target === modal) cerrarModal();
        }});
    """)

    # 6. Estructura de contenido final
    contenido = Div(
        alert_top,
        modal_estilos,
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
