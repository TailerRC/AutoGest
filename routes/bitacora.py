"""
routes/bitacora.py — View puro de Bitácora de Diagnóstico
=========================================================
Solo renderiza HTML. Lógica en controllers/bitacora_ctrl.py.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout

def render_bitacora_list(req, usuario, bitacoras, q="", page=1, total_pages=1, total_count=0):
    """Renderiza la lista de bitácoras de diagnóstico."""
    msg = req.query_params.get("msg", "")
    alert = Div(I(cls="fa-solid fa-circle-check"), " Bitácora registrada correctamente.", cls="alert alert-success") \
        if msg == "creado" else ""

    filter_form = Form(
        Div(
            Div(
                Label("Búsqueda"),
                Input(name="q", placeholder="Placa, código de diagnóstico o mecánico...", value=q),
                cls="form-group"
            ),
            Div(
                Label(style="visibility:hidden;"),
                Div(
                    Button(I(cls="fa-solid fa-magnifying-glass"), " Buscar", type="submit", cls="btn btn-primary"),
                    A(I(cls="fa-solid fa-filter-circle-xmark"), " Limpiar", href="/bitacora", cls="btn btn-secondary"),
                    style="display:flex; gap:0.5rem;"
                ),
                cls="form-group"
            ),
            cls="form-grid",
            style="margin-bottom:0.5rem; align-items: flex-end;"
        ),
        method="get", action="/bitacora",
        cls="filter-card",
        style="padding:1.25rem; background:var(--bg-page); border:1.5px solid var(--border); border-radius:var(--radius); margin-bottom:1.5rem;"
    )

    filas = []
    for b in bitacoras:
        sintomas_tags = Div(*[Span(s, cls="tag") for s in b.get("sintomas", [])], cls="tag-list")
        codigos = b.get("codigo_OBD", [])
        codigos_tags = Div(*[Span(c, cls="tag-obd") for c in codigos], cls="tag-list") \
            if codigos else Span("—", cls="text-muted")

        id_vehiculo = b.get("idVehiculo", "?")
        codigo_diag = b.get("codigoDiagnostico", "")

        filas.append(Tr(
            Td(Span(b.get("placa_vehiculo", f"#{id_vehiculo}"), cls="badge badge-gray font-mono")),
            Td(b.get("nombre_empleado", "—")),
            Td(sintomas_tags),
            Td(codigos_tags),
            Td(A(I(cls="fa-solid fa-eye"), " Ver", href=f"/bitacora/diagnostico/{codigo_diag}", cls="btn btn-sm btn-secondary")),
        ))

    crear_btn = A(I(cls="fa-solid fa-plus"), " Nueva Bitácora", href="/bitacora/nueva", cls="btn btn-primary") \
        if puede_acceder(usuario, "bitacora", "crear") else ""

    # ── Paginación (mismo patrón que Repuestos/Cotizaciones/Órdenes) ──
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

    query_str = f"&q={q}"
    page_buttons = []
    for p in range(start_page, end_page + 1):
        is_current = (p == page)
        btn_cls = "btn btn-sm btn-primary" if is_current else "btn btn-sm btn-secondary"
        page_buttons.append(A(str(p), href=f"/bitacora?page={p}{query_str}", cls=btn_cls, style="min-width:32px; text-align:center;"))

    if page > 1:
        pag_prev = A(I(cls="fa-solid fa-chevron-left"), " Anterior", href=f"/bitacora?page={page - 1}{query_str}", cls="btn btn-sm btn-secondary")
    else:
        pag_prev = Span(I(cls="fa-solid fa-chevron-left"), " Anterior", cls="btn btn-sm btn-secondary disabled", style="opacity:0.5; cursor:not-allowed;")

    if page < total_pages:
        pag_next = A("Siguiente ", I(cls="fa-solid fa-chevron-right"), href=f"/bitacora?page={page + 1}{query_str}", cls="btn btn-sm btn-secondary")
    else:
        pag_next = Span("Siguiente ", I(cls="fa-solid fa-chevron-right"), cls="btn btn-sm btn-secondary disabled", style="opacity:0.5; cursor:not-allowed;")

    start_item = (page - 1) * 6 + 1 if total_count > 0 else 0
    end_item = min(page * 6, total_count)

    paginacion = Div(
        Span(f"Mostrando {start_item}–{end_item} de {total_count} registros", cls="text-muted text-sm"),
        Div(pag_prev, *page_buttons, pag_next, cls="paginacion-nav"),
        cls="paginacion-container"
    )

    tabla = Div(
        Table(
            Thead(Tr(Th("Vehículo"), Th("Mecánico"), Th("Síntomas"), Th("Códigos OBD"), Th("Acciones"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("Sin bitácoras.", colspan="5", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    contenido = Div(
        alert,
        Div(
            Div(H2(I(cls="fa-solid fa-clipboard-list"), " Bitácora de Diagnóstico"), Span("MongoDB", cls="db-tag mongo"), cls="card-header"),
            Div(
                Div(Span(f"{total_count} registros", cls="text-muted text-sm"), crear_btn,
                    cls="flex gap-2", style="justify-content:space-between;align-items:center;margin-bottom:1rem;"),
                filter_form,
                tabla,
                paginacion,
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Bitácora", "Bitácora de Diagnóstico", "Base de datos MongoDB", contenido)


def render_bitacora_detalle(req, bitacora, vehiculo):
    """Renderiza el detalle de una bitácora."""
    if not bitacora:
        from fasthtml.common import RedirectResponse
        return RedirectResponse("/bitacora", status_code=303)

    id_vehiculo = bitacora.get("idVehiculo", "?")
    codigo_diagnostico = bitacora.get("codigoDiagnostico", "")
    vehiculo_desc = f"{vehiculo.get('marca','')} {vehiculo.get('modelo','')} — {vehiculo.get('placa','')}" if vehiculo else "—"
    sintomas = bitacora.get("sintomas", [])
    codigos  = bitacora.get("codigo_OBD", [])
    fotos    = bitacora.get("fotografias_url", [])

    msg   = req.query_params.get("msg", "")
    error = req.query_params.get("error", "")
    alert_foto = ""
    if msg == "fotos_ok":
        alert_foto = Div(I(cls="fa-solid fa-circle-check"), " Fotos guardadas correctamente.", cls="alert alert-success")
    elif error:
        alert_foto = Div(I(cls="fa-solid fa-triangle-exclamation"), f" {error}", cls="alert alert-error")

    contenido = Div(
        Div(
            Div(
                Div(
                    H2(I(cls="fa-solid fa-clipboard-list"), f" Bitácora — Vehículo #{id_vehiculo}"),
                    Span("MongoDB", cls="db-tag mongo"),
                ),
                A("← Volver", href="/bitacora", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(
                Div(
                    Div(Label("Vehículo Referencia"),    Div(f"#{id_vehiculo}", cls="detail-value font-mono"), cls="detail-item"),
                    Div(Label("ID Empleado"),            Div(str(bitacora.get("idEmpleado", "—")), cls="detail-value"), cls="detail-item"),
                    Div(Label("Cod. Especificación"),    Div(bitacora.get("codigoEspecificacion", "—"), cls="detail-value"), cls="detail-item"),
                    Div(Label("Vehículo Datos"),         Div(vehiculo_desc, cls="detail-value"), cls="detail-item"),
                    cls="detail-grid"
                ),
                Div(style="margin-top:1.5rem;"),
                Div(
                    Div(
                        Span(I(cls="fa-solid fa-stethoscope"), " Síntomas reportados", style="font-size:.75rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;"),
                        Div(*[Span(s, cls="tag") for s in sintomas], cls="tag-list mt-1") if sintomas else P("Sin síntomas.", cls="text-muted text-sm mt-1"),
                        style="margin-bottom:1.25rem;"
                    ),
                    Div(
                        Span(I(cls="fa-solid fa-triangle-exclamation"), " Códigos OBD detectados", style="font-size:.75rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;"),
                        Div(*[Span(c, cls="tag-obd") for c in codigos], cls="tag-list mt-1") if codigos else P("Sin códigos OBD.", cls="text-muted text-sm mt-1"),
                        style="margin-bottom:1.25rem;"
                    ),
                    Div(
                        Span(I(cls="fa-solid fa-file-lines"), " Observaciones", style="font-size:.75rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;"),
                        P(bitacora.get("observaciones", "—"), style="margin-top:.5rem;color:var(--text-secondary);font-size:.875rem;line-height:1.6;"),
                    ),
                ),
                Div(style="margin-top:1rem;"),
                Div(
                    Span(I(cls="fa-solid fa-image"), " Fotos adjuntas", style="font-size:.75rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;"),
                    Div(
                        *[
                            Button(
                                I(cls="fa-regular fa-image"), f" {foto.split('/')[-1].split(chr(92))[-1]}",
                                type="button",
                                cls="tag foto-tag-clicable",
                            )
                            for foto in fotos
                        ],
                        cls="tag-list mt-1"
                    ) if fotos else P("Sin fotos.", cls="text-muted text-sm mt-1"),
                ),
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        _seccion_fotos_bitacora(codigo_diagnostico, alert_foto) if len(fotos) == 0 else "",
        "",
        cls="page-body"
    )
    return layout(req, f"Bitácora {codigo_diagnostico}", f"Bitácora de Diagnóstico {codigo_diagnostico}", "", contenido)


def _modal_foto_preview():
    """Modal simple para previsualizar una foto de evidencia en grande."""
    return Div(
        Div(
            Div(
                Div(
                    H3(I(cls="fa-solid fa-image"), " Vista previa"),
                    Button("×", onclick="cerrarFotoModal()", cls="tech-modal-close"),
                    cls="tech-modal-header"
                ),
                Div(
                    Img(id="foto-modal-img", src="", style="max-width:100%;border-radius:8px;display:block;margin:0 auto;"),
                    cls="tech-modal-body"
                ),
                cls="tech-modal-content"
            ),
            id="foto-modal",
            cls="tech-modal"
        ),
        Script("""
            function abrirFotoModal(src) {
                document.getElementById('foto-modal-img').src = src;
                document.getElementById('foto-modal').classList.add('active');
            }
            function cerrarFotoModal() {
                document.getElementById('foto-modal').classList.remove('active');
            }
            window.addEventListener('click', function(e) {
                const modal = document.getElementById('foto-modal');
                if (e.target === modal) cerrarFotoModal();
            });
        """)
    )

def _seccion_fotos_bitacora(codigo_diagnostico, alert_foto):
    """Sección para subir las 3 fotos de evidencia de una bitácora (solo si aún no tiene)."""
    return Div(
        Div(
            H2(I(cls="fa-solid fa-camera"), " Fotos de Evidencia del Diagnóstico"),
            cls="card-header"
        ),
        Div(
            alert_foto,
            P(
                I(cls="fa-solid fa-circle-info"),
                f" Se guardarán en la carpeta: ",
                Span(f"{codigo_diagnostico}", cls="badge badge-gray font-mono"),
                cls="text-muted text-sm mb-2"
            ),
            Form(
                Div(
                    Div(
                        Label(I(cls="fa-solid fa-car-side"), " Vista Frontal"),
                        Input(type="file", name="foto_frontal", accept="image/*", required=True, id="bf_frontal"),
                        Div(id="bpreview_frontal", cls="foto-preview"),
                        cls="form-group"
                    ),
                    Div(
                        Label(I(cls="fa-solid fa-car"), " Vista Lateral"),
                        Input(type="file", name="foto_lateral", accept="image/*", required=True, id="bf_lateral"),
                        Div(id="bpreview_lateral", cls="foto-preview"),
                        cls="form-group"
                    ),
                    Div(
                        Label(I(cls="fa-solid fa-camera-rotate"), " Toma Angular"),
                        Input(type="file", name="foto_angular", accept="image/*", required=True, id="bf_angular"),
                        Div(id="bpreview_angular", cls="foto-preview"),
                        cls="form-group"
                    ),
                    cls="form-grid"
                ),
                Div(
                    Span(id="bfotos-status", cls="text-muted text-sm", style="align-self:center;"),
                    Button(I(cls="fa-solid fa-cloud-arrow-up"), " Subir Fotos",
                           type="submit", id="btn-subir-bfotos", cls="btn btn-primary", disabled=True),
                    cls="form-actions"
                ),
                method="post", action=f"/bitacora/diagnostico/{codigo_diagnostico}/fotos", enctype="multipart/form-data"
            ),
            Script("""
                const bids = ['bf_frontal', 'bf_lateral', 'bf_angular'];
                function bverificar() {
                    const listas = bids.filter(id => {
                        const el = document.getElementById(id);
                        return el && el.files && el.files.length > 0;
                    });
                    const btn = document.getElementById('btn-subir-bfotos');
                    const status = document.getElementById('bfotos-status');
                    const faltan = bids.length - listas.length;
                    btn.disabled = faltan > 0;
                    status.textContent = faltan === 0 ? '✓ Las 3 fotos están listas.' : `Faltan ${faltan} foto(s).`;
                }
                bids.forEach(id => {
                    const input = document.getElementById(id);
                    const preview = document.getElementById('bpreview_' + id.replace('bf_', ''));
                    input.addEventListener('change', () => {
                        preview.innerHTML = '';
                        if (input.files[0]) {
                            const img = document.createElement('img');
                            img.src = URL.createObjectURL(input.files[0]);
                            img.style.cssText = 'width:100%;height:110px;object-fit:cover;border-radius:8px;';
                            preview.appendChild(img);
                        }
                        bverificar();
                    });
                });
                document.addEventListener('DOMContentLoaded', bverificar);
            """),
            cls="card-body"
        ),
        cls="form-card fade-in", style="margin-top:1.25rem;"
    )

def render_bitacora_nueva(req, vehiculos, empleados, catalogo=None):
    """Renderiza el formulario de nueva bitácora."""
    import json
    error = req.query_params.get("error", "")
    alert = Div(f"❌ {error}", cls="alert alert-error") if error else ""

    catalogo = catalogo or []

    opts_v = [Option(f"#{v['id_vehiculo']} — {v.get('marca','?')} {v.get('modelo','')} / {v.get('placa','')}",
                     value=str(v["id_vehiculo"])) for v in vehiculos]
    opts_e = [Option(f"{e['nombre']} ({e['cargo']})",
                     value=str(e["id_empleado"])) for e in empleados]
    opts_c = [Option(f"{c.get('codigoEspecificacion','?')} — {c.get('marca','')} {c.get('modelo','')} ({c.get('anio','')})",
                     value=c.get("codigoEspecificacion","")) for c in catalogo]

    # Mapa código -> datos completos, para la previsualización instantánea en JS
    catalogo_dict = {c.get("codigoEspecificacion",""): c for c in catalogo}

    form = Form(
        alert,
        Div(
            Div(Label("Vehículo"),
                Select(Option("-- Seleccionar --", value=""), *opts_v, name="id_vehiculo", required=True),
                cls="form-group"),
            Div(Label("Mecánico responsable"),
                Select(Option("-- Seleccionar --", value=""), *opts_e, name="id_empleado", required=True),
                cls="form-group"),
            Div(
                Label("Código Especificación"),
                Select(Option("-- Seleccionar --", value=""), *opts_c, name="codigo_especificacion",
                       id="select-cod-espec", required=True,
                       onchange="mostrarPreviewCatalogo(this.value)"),
                cls="form-group"
            ),
            cls="form-grid"
        ),
        Div(id="preview-catalogo", style="margin-top:1rem;"),
        Div(
            Div(Label("Síntomas reportados (separados por coma)"),
                Input(name="sintomas", placeholder="Motor hace ruido, Vibración al frenar", required=True),
                cls="form-group full-width"),
            Div(Label("Códigos OBD detectados (separados por coma, dejar vacío si no aplica)"),
                Input(name="codigos_obd", placeholder="P0300, C0031"),
                cls="form-group full-width"),
            Div(Label("Observaciones"),
                Textarea(name="observaciones", placeholder="Observaciones detalladas del diagnóstico...", rows="5", required=True),
                cls="form-group full-width"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/bitacora", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Guardar Bitácora", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/bitacora/crear"
    )

    catalogo_script = Script(f"""
        const catalogoData = {json.dumps(catalogo_dict)};
        const iconosDetalle = {{
            motor: 'fa-solid fa-gear',
            aceite: 'fa-solid fa-oil-can',
            refrigerante: 'fa-solid fa-droplet',
            transmision: 'fa-solid fa-gears',
            bujias: 'fa-solid fa-bolt',
            bateria: 'fa-solid fa-car-battery',
            neumaticos: 'fa-solid fa-circle-dot',
            frenos: 'fa-solid fa-stop-circle'
        }};

        function mostrarPreviewCatalogo(codigo) {{
            const cont = document.getElementById('preview-catalogo');
            if (!codigo || !catalogoData[codigo]) {{
                cont.innerHTML = '';
                return;
            }}
            const c = catalogoData[codigo];
            const detalles = c.detalles_tecnicos || {{}};
            let itemsDetalles = '';
            for (const [clave, valor] of Object.entries(detalles)) {{
                const claveLower = clave.toLowerCase();
                const icono = iconosDetalle[claveLower] || 'fa-solid fa-circle-info';
                itemsDetalles += '<div class="catalogo-preview-item">' +
                    '<i class="' + icono + '"></i>' +
                    '<div class="catalogo-preview-item-text">' +
                    '<span class="catalogo-preview-key">' + clave.replace(/_/g, ' ') + '</span>' +
                    '<span class="catalogo-preview-val">' + valor + '</span>' +
                    '</div></div>';
            }}
            cont.innerHTML = `
                <div class="catalogo-preview-card fade-in">
                    <div class="catalogo-preview-header">
                        <i class="fa-solid fa-car-side"></i>
                        <strong>${{c.marca || '—'}} ${{c.modelo || '—'}}</strong>
                        <span class="badge badge-gray">${{c.anio || '—'}}</span>
                    </div>
                    <div class="catalogo-preview-body">${{itemsDetalles || '<span class="text-muted text-sm">Sin detalles técnicos registrados.</span>'}}</div>
                </div>
            `;
        }}
    """)

    contenido = Div(
        Div(
            Div(
                Div(H2(I(cls="fa-solid fa-clipboard-list"), " Nueva Bitácora de Diagnóstico"), Span("MongoDB", cls="db-tag mongo")),
                A(I(cls="fa-solid fa-arrow-left"), " Volver", href="/bitacora", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        catalogo_script,
        cls="page-body"
    )
    return layout(req, "Nueva Bitácora", "Nueva Bitácora", "Guardar en MongoDB", contenido)
