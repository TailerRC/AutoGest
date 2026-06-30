"""
routes/usuarios.py — View puro de Usuarios
==========================================
Solo renderiza HTML. Lógica en controllers/usuarios_ctrl.py.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout, badge_estado, badge_rol

ROLES = ["admin", "mecanico", "facturacion", "readonly"]

ROL_COLOR = {
    "admin":       "#7C3AED",
    "mecanico":    "#3B82F6",
    "facturacion": "#F59E0B",
    "readonly":    "#6B7280",
}


def _avatar(nombre: str, color: str = "#7A0C11"):
    """Círculo con la inicial del nombre, color consistente por usuario."""
    inicial = (nombre or "?").strip()[0].upper()
    return Div(
        inicial,
        style=(
            f"width:36px;height:36px;border-radius:50%;background:{color};"
            "color:#fff;display:flex;align-items:center;justify-content:center;"
            "font-weight:700;font-size:.85rem;flex-shrink:0;"
        )
    )


def render_usuarios_list(req, usuario, usuarios):
    """Renderiza la lista de usuarios del sistema."""
    msg = req.query_params.get("msg", "")
    alerts_map = {
        "creado": Div(
            Div(I(cls="fa-solid fa-circle-check"), " Usuario creado correctamente.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        ),
        "editado": Div(
            Div(I(cls="fa-solid fa-circle-check"), " Usuario actualizado correctamente.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-success alert-dismissible"
        ),
        "desactivado": Div(
            Div(I(cls="fa-solid fa-triangle-exclamation"), " Usuario desactivado.", cls="alert-message"),
            Button(I(cls="fa-solid fa-xmark"), type="button", cls="alert-close", onclick="this.parentElement.remove()"),
            cls="alert alert-warning alert-dismissible"
        ),
    }
    alert = alerts_map.get(msg, "")

    filas = []
    for u in usuarios:
        es_yo = u["username"] == usuario.get("username")
        color = ROL_COLOR.get(u["rol"], "#7A0C11")

        acciones = [
            A(
                I(cls="fa-solid fa-pen"),
                href=f"/usuarios/{u['id_usuario']}/editar",
                cls="btn-icon icon-edit",
                **{"data-tooltip": "Editar solo tu username" if es_yo else "Editar usuario"}
            )
        ]
        if not es_yo and u["estado"] == "activo":
            acciones.append(
                Form(
                    Input(type="hidden", name="id_usuario", value=str(u["id_usuario"])),
                    Button(
                        I(cls="fa-solid fa-ban"),
                        type="submit", cls="btn-icon icon-delete",
                        onclick="return confirm('¿Desactivar este usuario?')",
                        **{"data-tooltip": "Desactivar"}
                    ),
                    method="post", action="/usuarios/desactivar",
                    style="display:inline;"
                )
            )

        nombre_cell = Div(
            _avatar(u["nombre_empleado"], color),
            Div(
                Div(
                    u["username"],
                    Span("Tú", cls="badge badge-gray", style="font-size:.65rem;padding:.1rem .45rem;") if es_yo else "",
                    style="font-weight:600;display:flex;align-items:center;gap:.4rem;"
                ),
                Div(u["nombre_empleado"], style="font-size:.78rem;color:var(--text-muted);"),
            ),
            style="display:flex;align-items:center;gap:.65rem;"
        )

        filas.append(Tr(
            Td(Span(f"#{u['id_usuario']}", cls="font-mono", style="color:var(--text-muted);font-size:.82rem;")),
            Td(nombre_cell),
            Td(badge_rol(u["rol"])),
            Td(badge_estado(u["estado"])),
            Td(Div(*acciones, cls="row-actions", style="align-items:center;")),
            cls="usuario-row"
        ))

    tabla = Div(
        Style("""
            .usuario-row { transition: background .15s; }
            .usuario-row:hover { background: var(--brand-primary-light); }
        """),
        Table(
            Thead(Tr(Th("#"), Th("Usuario"), Th("Rol"), Th("Estado"), Th("Acciones"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("Sin usuarios registrados.", colspan="5", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    contenido = Div(
        alert,
        Div(
            Div(H2(I(cls="fa-solid fa-lock"), " Gestión de Usuarios"), cls="card-header"),
            Div(
                Div(
                    Span(f"{len(usuarios)} usuarios", cls="text-muted text-sm"),
                    A(I(cls="fa-solid fa-plus"), " Nuevo Usuario", href="/usuarios/nuevo", cls="btn btn-primary"),
                    cls="flex gap-2",
                    style="justify-content:space-between;align-items:center;margin-bottom:1rem;"
                ),
                tabla,
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Usuarios", "Gestión de Usuarios", "Accesos, roles y contraseñas - Admin", contenido)


def render_usuarios_nuevo(req, empleados):
    """
    Formulario de nuevo usuario, en 2 columnas:
      Columna A: Empleado (select) + Cargo (autocompletado por JS, solo lectura)
      Columna B: Username + Contraseña (visible) + Rol
    """
    error = req.query_params.get("error", "")
    alert = Div(
        Div(I(cls="fa-solid fa-circle-exclamation"), f" {error}", cls="alert-message"),
        cls="alert alert-error"
    ) if error else ""

    opts_e = [
        Option(e["nombre"], value=str(e["id_empleado"]),
               **{"data-cargo": e.get("cargo", "—")})
        for e in empleados
    ]

    form = Form(
        alert,
        Div(
            # Columna A: Empleado + Cargo
            Div(
                Div(
                    Label("Empleado"),
                    Select(Option("-- Seleccionar --", value=""), *opts_e,
                           name="id_empleado", id="select-empleado", required=True),
                    cls="form-group"
                ),
                Div(
                    Label("Cargo"),
                    Input(id="input-cargo", value="", readonly=True,
                          placeholder="Se completa al elegir un empleado",
                          style="background:var(--brand-secondary-light);color:var(--text-muted);"),
                    cls="form-group"
                ),
                cls="form-col"
            ),
            # Columna B: Username + Contraseña + Rol
            Div(
                Div(Label("Username"),
                    Input(name="username", placeholder="juan.perez", required=True, autocomplete="off"),
                    cls="form-group"),
                Div(Label("Contraseña"),
                    Input(name="password", type="text", placeholder="Escribe la contraseña",
                          required=True, autocomplete="off"),
                    cls="form-group"),
                Div(Label("Rol"),
                    Select(*[Option(r.capitalize(), value=r) for r in ROLES], name="rol", required=True),
                    cls="form-group"),
                cls="form-col"
            ),
            cls="form-grid-2col"
        ),
        Div(
            A("Cancelar", href="/usuarios", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Crear Usuario", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/usuarios/crear"
    )

    autocompletar_js = Script("""
        document.addEventListener('DOMContentLoaded', function () {
            const sel = document.getElementById('select-empleado');
            const cargo = document.getElementById('input-cargo');
            if (!sel || !cargo) return;
            sel.addEventListener('change', function () {
                const opt = sel.options[sel.selectedIndex];
                cargo.value = opt && opt.dataset.cargo ? opt.dataset.cargo : '';
            });
        });
    """)

    contenido = Div(
        Style("""
            .form-grid-2col {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 0 2rem;
                align-items: start;
            }
            .form-col { display: flex; flex-direction: column; gap: 1rem; }
            @media (max-width: 700px) {
                .form-grid-2col { grid-template-columns: 1fr; gap: 1rem; }
            }
        """),
        Div(
            Div(H2(I(cls="fa-solid fa-user-plus"), " Nuevo Usuario"),
                A(I(cls="fa-solid fa-arrow-left"), " Volver", href="/usuarios", cls="btn btn-secondary btn-sm"),
                cls="card-header"),
            Div(form, autocompletar_js, cls="card-body"),
            cls="form-card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nuevo Usuario", "Nuevo Usuario", "", contenido)


def render_usuarios_editar(req, usuario, u, empleados):
    """
    Formulario de edición, en 2 columnas:
      Columna A: Empleado + Cargo — solo informativos, no editables.
      Columna B: Username (+ Contraseña/Rol/Estado solo si NO es el propio usuario).
    """
    id_usuario = u["id_usuario"]
    es_yo = u["username"] == usuario.get("username")
    error = req.query_params.get("error", "")
    alert = Div(
        Div(I(cls="fa-solid fa-circle-exclamation"), f" {error}", cls="alert-message"),
        cls="alert alert-error"
    ) if error else ""

    empleado = next((e for e in empleados if e["id_empleado"] == u["id_empleado"]), None)
    nombre_empleado = empleado["nombre"] if empleado else u.get("nombre_empleado", "—")
    cargo_empleado  = empleado.get("cargo", "—") if empleado else "—"

    nota_propio = Div(
        I(cls="fa-solid fa-circle-info", style="color:var(--text-muted);"),
        " Solo puedes modificar tu nombre de usuario. Para cambiar tu contraseña, "
        "rol o estado, pide a otro administrador que lo haga.",
        style="font-size:.85rem;color:var(--text-muted);margin-bottom:1rem;"
              "display:flex;align-items:center;gap:.4rem;"
    ) if es_yo else ""

    campos_columna_b = [
        Div(Label("Username"),
            Input(name="username", value=u["username"], required=True),
            cls="form-group"),
    ]
    if not es_yo:
        campos_columna_b += [
            Div(Label("Nueva contraseña (dejar vacío = no cambiar)"),
                Input(name="password", type="text", placeholder="Escribe la nueva contraseña",
                      autocomplete="off"),
                cls="form-group"),
            Div(Label("Rol"),
                Select(*[Option(r.capitalize(), value=r, selected=(r == u["rol"])) for r in ROLES],
                       name="rol", required=True),
                cls="form-group"),
            Div(Label("Estado"),
                Select(
                    Option("Activo",   value="activo",   selected=(u["estado"] == "activo")),
                    Option("Inactivo", value="inactivo", selected=(u["estado"] == "inactivo")),
                    name="estado", required=True
                ),
                cls="form-group"),
        ]

    form = Form(
        alert,
        nota_propio,
        Div(
            Div(
                Div(Label("Empleado"), Div(nombre_empleado, cls="info-readonly"), cls="form-group"),
                Div(Label("Cargo"),    Div(cargo_empleado, cls="info-readonly"), cls="form-group"),
                cls="form-col"
            ),
            Div(*campos_columna_b, cls="form-col"),
            cls="form-grid-2col"
        ),
        Input(type="hidden", name="id_usuario", value=str(id_usuario)),
        Input(type="hidden", name="id_empleado", value=str(u["id_empleado"])),
        Div(
            A("Cancelar", href="/usuarios", cls="btn btn-secondary"),
            Button(I(cls="fa-solid fa-floppy-disk"), " Actualizar", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/usuarios/actualizar"
    )

    contenido = Div(
        Style("""
            .form-grid-2col { display:grid; grid-template-columns:1fr 1fr; gap:0 2rem; align-items:start; }
            .form-col { display:flex; flex-direction:column; gap:1rem; }
            .info-readonly {
                padding:.55rem .75rem; background:var(--brand-secondary-light);
                border:1px solid var(--border); border-radius:8px;
                color:var(--text-secondary); font-size:.9rem;
            }
            @media (max-width:700px) { .form-grid-2col { grid-template-columns:1fr; gap:1rem; } }
        """),
        Div(
            Div(H2(I(cls="fa-solid fa-pen"), f" Editar Usuario: {u['username']}"),
                A(I(cls="fa-solid fa-arrow-left"), " Volver", href="/usuarios", cls="btn btn-secondary btn-sm"),
                cls="card-header"),
            Div(form, cls="card-body"),
            cls="form-card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Editar Usuario", f"Editar Usuario: {u['username']}", "", contenido)