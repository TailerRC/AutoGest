"""
routes/empleados.py — View puro de Empleados
=============================================
Solo renderiza HTML. Lógica en controllers/empleados_ctrl.py.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout
import json

ESPECIALIDADES_POR_CARGO = {
    "Jefe de Taller":            ["Gestión de Taller", "Administración General", "Mecánica General"],
    "Mecánico Senior":           ["Motor y Transmisión", "Diagnóstico Electrónico", "Frenos y Suspensión", "Suspensión y Dirección", "Mecánica General"],
    "Mecánico":                  ["Mecánica General", "Frenos y Suspensión", "Suspensión y Dirección", "Carrocería y Pintura", "Sistemas de Escape", "Soldadura Automotriz", "Aire Acondicionado Automotriz"],
    "Electricista Automotriz":   ["Electricidad Automotriz", "Diagnóstico Electrónico", "Aire Acondicionado Automotriz"],
    "Asistente Administrativo":  ["Gestión y Facturación", "Administración General", "Logística y Proveedores"],
    "Asesor de Ventas":          ["Ventas de Vehículos", "Atención al Cliente"],
    "Recepcionista":             ["Recepción y Despacho", "Atención al Cliente"],
}

ESPECIALIDADES = sorted({e for esp in ESPECIALIDADES_POR_CARGO.values() for e in esp})

CARGOS = [
    "Jefe de Taller", "Mecánico Senior", "Mecánico", "Electricista Automotriz",
    "Asistente Administrativo", "Asesor de Ventas", "Recepcionista"
]


def render_empleados_list(req, usuario, empleados, total, page, per_page, buscar=""):
    """Renderiza la lista de empleados."""
    msg = req.query_params.get("msg", "")
    alert_map = {
        "creado": Div(
            Div(I(cls="fa-solid fa-circle-check"), " Empleado registrado correctamente.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        ),
        "editado": Div(
            Div(I(cls="fa-solid fa-circle-check"), " Empleado actualizado correctamente.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        ),
        "eliminado": Div(
            Div(I(cls="fa-solid fa-trash"), " Empleado eliminado.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-warning alert-dismissible"
        ),
        "error": Div(
            Div(I(cls="fa-solid fa-circle-exclamation"), " Ocurrió un error al intentar eliminar el empleado.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-error alert-dismissible"
        ),
        "con_ordenes": Div(
            Div(
                I(cls="fa-solid fa-triangle-exclamation"),
                " No se puede eliminar este empleado porque tiene órdenes de trabajo asociadas.",
                cls="alert-message"
            ),
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
        b = f"&buscar={buscar}" if buscar else ""
        return f"/empleados?page={p}&per_page={pp}{m}{b}"

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
                f"Mostrando {(page-1)*per_page + 1}–{min(page*per_page, total)} de {total} empleados",
                cls="text-muted text-sm"
            ),
            selector_pp,
            cls="flex gap-2", style="align-items:center;justify-content:space-between;"
        ),
        Div(*paginas, cls="flex gap-1", style="justify-content:center;align-items:center;margin-top:.75rem;"),
        style="margin-top:1rem;padding-top:1rem;border-top:1px solid var(--border);"
    )
    filas = []
    for e in empleados:
        acciones = []
        if puede_acceder(usuario, "empleados", "editar"):
            acciones.append(
                A(
                    I(cls="fa-solid fa-pen"),
                    href=f"/empleados/{e['id_empleado']}/editar",
                    cls="btn-icon icon-edit",
                    **{"data-tooltip": "Editar"}
                )
            )
        if puede_acceder(usuario, "empleados", "eliminar"):
            nombre_modal = e["nombre"]
            acciones.append(
                Form(
                    Input(type="hidden", name="id_empleado", value=str(e["id_empleado"])),
                    Button(
                        I(cls="fa-solid fa-trash"),
                        type="button",
                        cls="btn-icon icon-delete",
                        **{"data-tooltip": "Eliminar"},
                        onclick=(
                            "confirmarEliminar(this, {"
                            "titulo: '¿Eliminar empleado?',"
                            "mensaje: 'Esta acción no se puede deshacer.',"
                            f"nombre: '{nombre_modal}'"
                            "})"
                        )
                    ),
                    method="post", action="/empleados/eliminar"
                )
            )

        # Badge de ID con icono de persona al hover
        id_badge = Div(
            I(cls="fa-solid fa-user-tie empleado-icon"),
            Span(f"#{e['id_empleado']}", cls="empleado-id-texto"),
            cls="empleado-id-badge"
        )

        filas.append(Tr(
            Td(id_badge, cls="td-empleado-id"),
            Td(e["nombre"]),
            Td(
                Div(
                    I(cls=f"fa-solid {_cargo_icon(e['cargo'])} cargo-icon"),
                    Span(e["cargo"], cls="cargo-texto"),
                    cls="cargo-cell"
                )
            ),
            Td(
                Span(e["especialidad"], cls="badge badge-blue")
                if e.get("especialidad") and e["especialidad"].strip()
                else Span("—", cls="text-muted text-sm")
            ),
            Td(Div(*acciones, cls="row-actions") if acciones else "—"),
            data_cargo=e["cargo"],
        ))

    tabla = Div(
        Table(
            Thead(Tr(
                Th("#"),
                Th("Nombre"),
                Th("Cargo"),
                Th("Especialidad"),
                Th("Acciones")
            )),
            Tbody(*filas) if filas else Tbody(
                Tr(Td("No hay empleados registrados.", colspan="5", cls="no-data"))
            ),
            id="tabla-empleados",
        ),
        cls="table-wrap"
    )

    crear_btn = A(
        I(cls="fa-solid fa-plus"), " Nuevo Empleado",
        href="/empleados/nuevo", cls="btn btn-primary"
    ) if puede_acceder(usuario, "empleados", "crear") else ""

    btn_filtro = Form(
        I(cls="fa-solid fa-magnifying-glass", style="position:absolute;left:.7rem;top:50%;transform:translateY(-50%);color:var(--text-muted);font-size:.8rem;"),
        Input(
            type="text",
            name="buscar",
            id="input-filtro-cargo",
            placeholder="Buscar por cargo...",
            value=buscar,
            oninput="debounceFiltro(this.value)",
            style="padding:.45rem .75rem .45rem 2rem;border:1px solid var(--border);border-radius:8px;font-size:.85rem;width:220px;"
        ),
        Input(type="hidden", name="per_page", value=str(per_page)),
        method="get", action="/empleados",
        style="position:relative;display:inline-block;"
    )

    contenido = Div(
        Style("""
            .empleado-id-badge {
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

            .empleado-icon {
                font-size: .85rem;
                max-width: 0;
                opacity: 0;
                overflow: hidden;
                transition: max-width .25s ease, opacity .2s ease, margin-right .25s ease;
                margin-right: 0;
                color: var(--brand-primary);
            }

            tr:hover .empleado-id-badge {
                background: var(--brand-primary-light);
                border-color: rgba(122,12,17,.3);
                color: var(--brand-primary);
                box-shadow: 0 2px 8px rgba(122,12,17,.12);
            }

            tr:hover .empleado-icon {
                max-width: 20px;
                opacity: 1;
                margin-right: .4rem;
            }

            .td-empleado-id { width: 80px; }
              
            .cargo-cell {
                display: inline-flex;
                align-items: center;
                gap: .45rem;
            }

            .cargo-icon {
                font-size: .78rem;
                color: var(--brand-secondary);
                opacity: .7;
                flex-shrink: 0;
            }

            .cargo-texto {
                font-size: .85rem;
                font-weight: 500;
                color: var(--text-primary);
            }  
        """),
        Script("""
            let timeoutFiltro;
            function debounceFiltro(valor) {
                clearTimeout(timeoutFiltro);
                timeoutFiltro = setTimeout(() => {
                    const params = new URLSearchParams(window.location.search);
                    params.set('buscar', valor);
                    params.set('page', '1');
                    window.location.search = params.toString();
                }, 500);
            }
        """),
        alert,
        Div(
            Div(H2(I(cls="fa-solid fa-users-gear"), " Empleados"), cls="card-header"),
            Div(
                Div(
                    Span(f"{total} empleados", cls="text-muted text-sm"),  # ← total
                    Div(btn_filtro, crear_btn, cls="flex gap-2", style="align-items:center;"),
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
    return layout(req, "Empleados", "Gestión de Empleados", "Añadir, Eliminar y Agregar Empleados", contenido)

def _cargo_icon(cargo: str) -> str:
    iconos = {
        "Jefe de Taller":            "fa-star",
        "Mecánico Senior":           "fa-wrench",
        "Mecánico":                  "fa-screwdriver-wrench",
        "Electricista Automotriz":   "fa-bolt",
        "Asistente Administrativo":  "fa-file-lines",
        "Asesor de Ventas":          "fa-handshake",
        "Recepcionista":             "fa-headset",
    }
    return iconos.get(cargo, "fa-circle-user")

def render_empleados_nuevo(req):
    error = req.query_params.get("error", "")
    alert = Div(
        I(cls="fa-solid fa-circle-exclamation"), f" {error}",
        cls="alert alert-error"
    ) if error else ""

    form = Form(
        alert,
        Div(
            Div(
                Label("Nombre completo"),
                Input(name="nombre", placeholder="Luis Alberto Romero", required=True),
                cls="form-group"
            ),
            Div(
                Label("Cargo"),
                Select(
                    *[Option(c, value=c) for c in ESPECIALIDADES_POR_CARGO.keys()],
                    name="cargo",
                    required=True,
                    id="sel-cargo",
                    onchange="filtrarEspecialidades(this.value)"
                ),
                cls="form-group"
            ),
            Div(
                Label("Especialidad"),
                Select(name="especialidad", required=True, id="sel-especialidad"),
                cls="form-group"
            ),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/empleados", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Guardar Empleado", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/empleados/crear"
    ),
    Script(f"""
        const MAPA = {json.dumps(ESPECIALIDADES_POR_CARGO)};

        function filtrarEspecialidades(cargo) {{
            const sel = document.getElementById('sel-especialidad');
            const opciones = MAPA[cargo] || [];
            sel.innerHTML = opciones
                .map(e => `<option value="${{e}}">${{e}}</option>`)
                .join('');
        }}

        // Inicializar con el primer cargo al cargar
        document.addEventListener('DOMContentLoaded', () => {{
            const cargo = document.getElementById('sel-cargo').value;
            if (cargo) filtrarEspecialidades(cargo);
        }});
    """)

    contenido = Div(
            Div(
                Div(
                    H2(I(cls="fa-solid fa-user-plus"), " Nuevo Empleado"),
                    A(I(cls="fa-solid fa-arrow-left"), " Volver", href="/empleados", cls="btn btn-secondary btn-sm"),
                    cls="card-header"
                ),
                Div(
                    Form(
                        alert,
                        Div(
                            Div(Label("Nombre completo"), Input(name="nombre", placeholder="Luis Alberto Romero", required=True), cls="form-group"),
                            Div(
                                Label("Cargo"),
                                Select(*[Option(c, value=c) for c in ESPECIALIDADES_POR_CARGO.keys()],
                                    name="cargo", required=True, id="sel-cargo",
                                    onchange="filtrarEspecialidades(this.value)"),
                                cls="form-group"
                            ),
                            Div(Label("Especialidad"), Select(name="especialidad", required=True, id="sel-especialidad"), cls="form-group"),
                            cls="form-grid"
                        ),
                        Div(
                            A("Cancelar", href="/empleados", cls="btn btn-secondary"),
                            Button(I(cls="fa-solid fa-floppy-disk"), " Guardar Empleado", type="submit", cls="btn btn-primary"),
                            cls="form-actions"
                        ),
                        method="post", action="/empleados/crear"
                    ),
                    Script(f"""
                        const MAPA = {json.dumps(ESPECIALIDADES_POR_CARGO)};
                        function filtrarEspecialidades(cargo) {{
                            const sel = document.getElementById('sel-especialidad');
                            const opciones = MAPA[cargo] || [];
                            sel.innerHTML = opciones.map(e => `<option value="${{e}}">${{e}}</option>`).join('');
                        }}
                        document.addEventListener('DOMContentLoaded', () => {{
                            const cargo = document.getElementById('sel-cargo').value;
                            if (cargo) filtrarEspecialidades(cargo);
                        }});
                    """),
                    cls="card-body"
                ),
                cls="form-card fade-in"
            ),
            cls="page-body"
        )
    return layout(req, "Nuevo Empleado", "Nuevo Empleado", "Incorporación de Nuevos Empleados", contenido)


def render_empleados_editar(req, empleado):
    id_empleado = empleado["id_empleado"]
    cargo_actual = empleado["cargo"]
    especialidad_actual = empleado.get("especialidad", "")

    form = Form(
        Div(
            Div(
                Label("Nombre completo"),
                Input(name="nombre", value=empleado["nombre"], required=True),
                cls="form-group"
            ),
            Div(
                Label("Cargo"),
                Select(
                    *[Option(c, value=c, selected=(c == cargo_actual))
                      for c in ESPECIALIDADES_POR_CARGO.keys()],
                    name="cargo",
                    required=True,
                    id="sel-cargo",
                    onchange="filtrarEspecialidades(this.value)"
                ),
                cls="form-group"
            ),
            Div(
                Label("Especialidad"),
                Select(name="especialidad", required=True, id="sel-especialidad"),
                cls="form-group"
            ),
            cls="form-grid"
        ),
        Input(type="hidden", name="id_empleado", value=str(id_empleado)),
        Div(
            A("Cancelar", href="/empleados", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Actualizar", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/empleados/actualizar"
    ),
    Script(f"""
        const MAPA = {json.dumps(ESPECIALIDADES_POR_CARGO)};
        const ACTUAL = "{especialidad_actual}";

        function filtrarEspecialidades(cargo) {{
            const sel = document.getElementById('sel-especialidad');
            const opciones = MAPA[cargo] || [];
            sel.innerHTML = opciones
                .map(e => `<option value="${{e}}" ${{e === ACTUAL ? 'selected' : ''}}>${{e}}</option>`)
                .join('');
        }}

        document.addEventListener('DOMContentLoaded', () => {{
            filtrarEspecialidades("{cargo_actual}");
        }});
    """)

    contenido = Div(
        Div(
            Div(
                H2(I(cls="fa-solid fa-pen"), f" Editar Empleado #{id_empleado}"),
                A(I(cls="fa-solid fa-arrow-left"), " Volver", href="/empleados", cls="btn btn-secondary btn-sm"),
                cls="card-header"
            ),
            Div(
                Form(
                    Div(
                        Div(Label("Nombre completo"), Input(name="nombre", value=empleado["nombre"], required=True), cls="form-group"),
                        Div(
                            Label("Cargo"),
                            Select(*[Option(c, value=c, selected=(c == cargo_actual)) for c in ESPECIALIDADES_POR_CARGO.keys()],
                                   name="cargo", required=True, id="sel-cargo",
                                   onchange="filtrarEspecialidades(this.value)"),
                            cls="form-group"
                        ),
                        Div(Label("Especialidad"), Select(name="especialidad", required=True, id="sel-especialidad"), cls="form-group"),
                        cls="form-grid"
                    ),
                    Input(type="hidden", name="id_empleado", value=str(id_empleado)),
                    Div(
                        A("Cancelar", href="/empleados", cls="btn btn-secondary"),
                        Button(I(cls="fa-solid fa-floppy-disk"), " Actualizar", type="submit", cls="btn btn-primary"),
                        cls="form-actions"
                    ),
                    method="post", action="/empleados/actualizar"
                ),
                Script(f"""
                    const MAPA = {json.dumps(ESPECIALIDADES_POR_CARGO)};
                    const ACTUAL = "{especialidad_actual}";
                    function filtrarEspecialidades(cargo) {{
                        const sel = document.getElementById('sel-especialidad');
                        const opciones = MAPA[cargo] || [];
                        sel.innerHTML = opciones
                            .map(e => `<option value="${{e}}" ${{e === ACTUAL ? 'selected' : ''}}>${{e}}</option>`)
                            .join('');
                    }}
                    document.addEventListener('DOMContentLoaded', () => {{
                        filtrarEspecialidades("{cargo_actual}");
                    }});
                """),
                cls="card-body"
            ),
            cls="form-card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Editar Empleado", f"Editar Empleado #{id_empleado}", "", contenido)