"""
routes/historial.py
===================
Vista para Historial de Mantenimiento.
"""
import json
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout


def badge_estado_historial(estado: str):
    """
    Genera un badge formateado y coloreado según las convenciones
    del taller para los estados de mantenimiento.
    """
    est_lower = estado.lower() if estado else ""
    if est_lower == "reparado":
        return Span(I(cls="fa-solid fa-circle-check"), " Reparado", cls="badge badge-green")
    elif est_lower == "observado":
        return Span(I(cls="fa-solid fa-triangle-exclamation"), " Observado", cls="badge badge-yellow")
    elif est_lower == "pendiente":
        return Span(I(cls="fa-solid fa-clock"), " Pendiente", cls="badge badge-gray")
    return Span(estado, cls="badge badge-gray")


def render_historial_list(req, usuario, historiales, q="", estado="todos", orden="fecha_desc", page=1, total_pages=1, total_count=0):
    """
    Renderiza la vista principal del listado de historial con filtros, búsqueda,
    paginación numérica y modal de detalles.
    """
    filas = []
    for h in historiales:
        detalles = h.get("diagnosticos_detalle", [])
        cantidad = len(detalles)
        tags_diag = [
            Span(
                I(cls="fa-solid fa-stethoscope"),
                f" {cantidad} diagnóstico{'s' if cantidad != 1 else ''}",
                cls="tag",
                title=", ".join(d["codigoDiagnostico"] for d in detalles)  # tooltip con los códigos
            )
        ] if detalles else []
                
        acciones = [
            Button(
                I(cls="fa-solid fa-eye"), " Ver Historial",
                onclick=f"verHistorial('{str(h['_id'])}')",
                cls="btn btn-sm btn-secondary",
                title="Ver Ficha de Historial",
                style="padding: 0.35rem 0.7rem; font-size: 0.8rem;"
            )
        ]

        filas.append(Tr(
            Td(Span(h.get("vehiculo_str", "—"), style="font-weight:600; color:var(--text-primary);"), data_label="Vehículo"),
            Td(f"{h.get('kilometraje_ingreso', 0):,} km", data_label="Kilometraje"),
            Td(h.get("fecha_servicio_str", "—"), data_label="Fecha Servicio"),
            Td(Div(*tags_diag, cls="tag-list") if tags_diag else "—", data_label="Diagnósticos"),
            Td(badge_estado_historial(h.get("estado_final", "pendiente")), data_label="Estado"),
            Td(Div(*acciones, cls="flex gap-1") if acciones else "—", data_label="Acciones")
        ))

    crear_btn = (
        A(
            I(cls="fa-solid fa-plus"), " Nuevo Registro",
            href="/historial/nuevo",
            cls="btn btn-primary"
        )
        if puede_acceder(usuario, "historial", "crear")
        else ""
    )

    tabla = Div(
        Table(
            Thead(Tr(
                Th("Vehículo (Oracle)"),
                Th("Kilometraje"),
                Th("Fecha Servicio"),
                Th("Diagnósticos"),
                Th("Estado"),
                Th("Acciones")
            )),
            Tbody(*filas) if filas else Tbody(Tr(Td("No se encontraron registros en el historial.", colspan="6", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    # Panel de Búsqueda y Filtros
    estados_opciones = ["Todos", "Reparado", "Observado", "Pendiente"]
    select_estados = [
        Option(opt, value=opt.lower() if opt != "Todos" else "todos", selected=(estado == (opt.lower() if opt != "Todos" else "todos")))
        for opt in estados_opciones
    ]

    orden_opciones = [
        ("Fecha reciente", "fecha_desc"),
        ("Fecha antigua", "fecha_asc"),
        ("Mayor kilometraje", "km_desc"),
        ("Menor kilometraje", "km_asc")
    ]
    select_orden = [
        Option(opt_label, value=opt_val, selected=(orden == opt_val))
        for opt_label, opt_val in orden_opciones
    ]

    filter_form = Form(
        Div(
            Div(
                Label("Búsqueda"),
                Input(name="q", placeholder="Vehículo, placa, diagnóstico, fecha...", value=q),
                cls="form-group"
            ),
            Div(
                Label("Estado"),
                Select(*select_estados, name="estado"),
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
                    A(I(cls="fa-solid fa-filter-circle-xmark"), " Limpiar", href="/historial", cls="btn btn-secondary"),
                    style="display:flex; gap:0.5rem;"
                ),
                cls="form-group"
            ),
            cls="form-grid",
            style="margin-bottom:0.5rem; align-items: flex-end;"
        ),
        method="get", action="/historial",
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
    query_str = f"&q={q}&estado={estado}&orden={orden}"
    for p in range(start_page, end_page + 1):
        is_current = (p == page)
        btn_cls = "btn btn-sm btn-primary" if is_current else "btn btn-sm btn-secondary"
        page_buttons.append(
            A(
                str(p),
                href=f"/historial?page={p}{query_str}",
                cls=btn_cls,
                style="min-width:32px; text-align:center;"
            )
        )

    # Paginación Anterior / Siguiente
    if page > 1:
        pag_prev = A(
            I(cls="fa-solid fa-chevron-left"), " Anterior",
            href=f"/historial?page={page - 1}{query_str}",
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
            href=f"/historial?page={page + 1}{query_str}",
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

    # Modal para ver la Ficha de Historial
    modal = Div(
        Div(
            Div(
                H3(I(cls="fa-solid fa-clock-rotate-left"), " Ficha de Historial de Mantenimiento"),
                Button("×", onclick="cerrarModal()", cls="tech-modal-close"),
                cls="tech-modal-header"
            ),
            Div(
                Div(
                    Div(Label("Vehículo"), Div(id="modal-vehiculo", cls="tech-val"), cls="tech-item"),
                    Div(Label("Placa"), Div(id="modal-placa", cls="tech-val"), cls="tech-item"),
                    Div(Label("Fecha de Servicio"), Div(id="modal-fecha", cls="tech-val"), cls="tech-item"),
                    Div(Label("Kilometraje"), Div(id="modal-kilometraje", cls="tech-val"), cls="tech-item"),
                    Div(Label("Estado Final"), Div(id="modal-estado", cls="tech-val"), cls="tech-item"),
                    cls="tech-grid"
                ),
                # Sección diagnósticos expandible
                Div(
                    H4(I(cls="fa-solid fa-stethoscope"), " Diagnósticos Asociados",
                    style="margin: 1rem 0 0.5rem; font-size:0.95rem; color:var(--text-primary);"),
                    Div(id="modal-diagnosticos-lista"),
                    cls=""
                ),
                cls="tech-modal-body"
            ),
            cls="tech-modal-content"
        ),
        id="tech-modal",
        cls="tech-modal"
    )

    # Serializar historial completo para consulta JS del modal
    historial_dict = {}
    for h in historiales:
        detalles = h.get("diagnosticos_detalle", [])
        
        diags_serializados = [
            {
                "codigo": d.get("codigoDiagnostico", "—"),
                "especificacion": d.get("codigoEspecificacion", "—"),
                "sintomas": ", ".join(d.get("sintomas", [])) or "—",
                "obd": ", ".join(d.get("codigo_OBD", [])) or "—",
                "observaciones": d.get("observaciones", "—"),
            }
            for d in detalles
        ]

        historial_dict[str(h["_id"])] = {
            "vehiculo": h.get("vehiculo_str", "—"),
            "placa": h.get("placa", "—"),
            "fecha": h.get("fecha_servicio_str", "—"),
            "kilometraje": f"{h.get('kilometraje_ingreso', 0):,} km",
            "estado": h.get("estado_final", "—"),
            "diagnosticos": diags_serializados,
        }

    js_script = Script(f"""
        const historyData = {json.dumps(historial_dict)};
        
        function verHistorial(id) {{
            const data = historyData[id];
            if (!data) return;
            
            document.getElementById('modal-vehiculo').innerText = data.vehiculo;
            document.getElementById('modal-placa').innerText = data.placa;
            document.getElementById('modal-fecha').innerText = data.fecha;
            document.getElementById('modal-kilometraje').innerText = data.kilometraje;
            document.getElementById('modal-estado').innerText = data.estado;
            
            // Renderizar diagnósticos
            const lista = document.getElementById('modal-diagnosticos-lista');
            if (!data.diagnosticos || data.diagnosticos.length === 0) {{
                lista.innerHTML = '<p style="color:var(--text-muted); font-size:0.85rem;">Sin diagnósticos asociados.</p>';
            }} else {{
                lista.innerHTML = data.diagnosticos.map(d => `
                    <div style="border:1px solid var(--border); border-radius:var(--radius); padding:0.75rem 1rem; margin-bottom:0.6rem; background:var(--bg-page);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                            <span style="font-weight:700; color:var(--text-primary); font-size:0.9rem;">
                                <i class="fa-solid fa-tag"></i> ${{d.codigo}}
                            </span>
                            <span style="font-size:0.78rem; color:var(--text-muted);">${{d.especificacion}}</span>
                        </div>
                        <div style="font-size:0.82rem; color:var(--text-secondary); display:grid; gap:0.2rem;">
                            <span><b>Síntomas:</b> ${{d.sintomas}}</span>
                            <span><b>Códigos OBD:</b> ${{d.obd}}</span>
                            <span><b>Observaciones:</b> ${{d.observaciones}}</span>
                        </div>
                    </div>
                `).join('');
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

    msg = req.query_params.get("msg", "")
    alert = Div(I(cls="fa-solid fa-circle-check"), " Registro de historial añadido exitosamente.", cls="alert alert-success") if msg == "creado" else ""

    contenido = Div(
        alert,
        Div(
            Div(
                H2(I(cls="fa-solid fa-clock-rotate-left"), " Historial de Mantenimiento"),
                Span("MongoDB", cls="db-tag mongo"),
                cls="card-header"
            ),
            Div(
                Div(
                    P("Colección que almacena el recorrido histórico de mantenimientos de un vehículo.", cls="text-muted text-sm"),
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
        modal,
        js_script,
        cls="page-body"
    )
    return layout(req, "Historial", "Historial de Mantenimiento", "Base de datos MongoDB", contenido)


def render_historial_nuevo(req, vehiculos):
    """
    Renderiza el formulario independiente para crear un registro en el historial.
    """
    error = req.query_params.get("error", "")
    alert = Div(I(cls="fa-solid fa-circle-exclamation"), f" {error}", cls="alert alert-error") if error else ""

    opts_v = [Option(f"#{v['id_vehiculo']} — {v.get('marca','')} {v.get('modelo','')} ({v.get('placa','')})", value=str(v["id_vehiculo"])) for v in vehiculos]

    form = Form(
        alert,
        Div(
            Div(Label("Vehículo"), Select(Option("-- Seleccionar --", value=""), *opts_v, name="id_vehiculo", required=True), cls="form-group"),
            Div(Label("Kilometraje de Ingreso"), Input(name="kilometraje_ingreso", type="number", min="0", placeholder="50000", required=True), cls="form-group"),
            Div(Label("Fecha de Servicio"), Input(name="fecha_servicio", type="date", required=True), cls="form-group"),
            Div(Label("Estado Final"), 
                Select(
                    Option("Reparado", value="Reparado"),
                    Option("Observado", value="Observado"),
                    Option("Pendiente", value="Pendiente"),
                    name="estado_final", required=True
                ), 
                cls="form-group"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/historial", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Guardar Registro", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/historial/crear"
    )

    contenido = Div(
        Div(
            Div(
                H2(I(cls="fa-solid fa-plus"), " Nuevo Registro de Historial"),
                A("← Volver", href="/historial", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nuevo Historial", "Nuevo Registro de Historial", "", contenido)
