"""
routes/empleados.py — View puro de Empleados
=============================================
Solo renderiza HTML. Lógica en controllers/empleados_ctrl.py.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout

ESPECIALIDADES = [
    "Mecánica General", "Motor y Transmisión", "Electricidad Automotriz",
    "Frenos y Suspensión", "Carrocería y Pintura", "Gestión y Facturación",
    "Diagnóstico Electrónico", "Aire Acondicionado Automotriz"
]

CARGOS = [
    "Jefe de Taller", "Mecánico Senior", "Mecánico", "Electricista Automotriz",
    "Asistente Administrativo", "Asesor de Ventas", "Recepcionista"
]


def render_empleados_list(req, usuario, empleados):
    """Renderiza la lista de empleados."""
    msg = req.query_params.get("msg", "")
    alert_map = {
        "creado":  Div("✅ Empleado registrado.", cls="alert alert-success"),
        "editado": Div("✅ Empleado actualizado.", cls="alert alert-success"),
    }
    alert = alert_map.get(msg, "")

    filas = []
    for e in empleados:
        acciones = []
        if puede_acceder(usuario, "empleados", "editar"):
            acciones.append(A("✏️ Editar", href=f"/empleados/{e['id_empleado']}/editar", cls="btn btn-sm btn-blue"))
        filas.append(Tr(
            Td(f"#{e['id_empleado']}", cls="font-mono text-muted text-sm"),
            Td(e["nombre"]),
            Td(e["cargo"]),
            Td(Span(e["especialidad"], cls="badge badge-blue")),
            Td(Div(*acciones, cls="flex gap-1") if acciones else "—"),
        ))

    tabla = Div(
        Table(
            Thead(Tr(Th("#"), Th("Nombre"), Th("Cargo"), Th("Especialidad"), Th("Acciones"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("Sin empleados.", colspan="5", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    crear_btn = A("＋ Nuevo Empleado", href="/empleados/nuevo", cls="btn btn-primary") \
        if puede_acceder(usuario, "empleados", "crear") else ""

    contenido = Div(
        alert,
        Div(
            Div(H2("👨‍🔧 Empleados"), cls="card-header"),
            Div(
                Div(Span(f"{len(empleados)} empleados", cls="text-muted text-sm"), crear_btn,
                    cls="flex gap-2", style="justify-content:space-between;align-items:center;margin-bottom:1rem;"),
                tabla, cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Empleados", "👨‍🔧 Gestión de Empleados", "Base de datos Oracle", contenido)


def render_empleados_nuevo(req):
    """Renderiza el formulario de nuevo empleado."""
    error = req.query_params.get("error", "")
    alert = Div(f"❌ {error}", cls="alert alert-error") if error else ""

    form = Form(
        alert,
        Div(
            Div(Label("Nombre completo"), Input(name="nombre", placeholder="Luis Alberto Romero", required=True), cls="form-group"),
            Div(Label("Cargo"),
                Select(*[Option(c, value=c) for c in CARGOS], name="cargo", required=True),
                cls="form-group"),
            Div(Label("Especialidad"),
                Select(*[Option(e, value=e) for e in ESPECIALIDADES], name="especialidad", required=True),
                cls="form-group"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/empleados", cls="btn btn-secondary"),
            Button("💾 Guardar", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/empleados/crear"
    )

    contenido = Div(
        Div(
            Div(H2("👤 Nuevo Empleado"), A("← Volver", href="/empleados", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nuevo Empleado", "👤 Nuevo Empleado", "", contenido)


def render_empleados_editar(req, empleado):
    """Renderiza el formulario de edición de un empleado."""
    id_empleado = empleado["id_empleado"]
    form = Form(
        Div(
            Div(Label("Nombre completo"), Input(name="nombre", value=empleado["nombre"], required=True), cls="form-group"),
            Div(Label("Cargo"),
                Select(*[Option(c, value=c, selected=(c == empleado["cargo"])) for c in CARGOS],
                       name="cargo", required=True),
                cls="form-group"),
            Div(Label("Especialidad"),
                Select(*[Option(es, value=es, selected=(es == empleado["especialidad"])) for es in ESPECIALIDADES],
                       name="especialidad", required=True),
                cls="form-group"),
            cls="form-grid"
        ),
        Input(type="hidden", name="id_empleado", value=str(id_empleado)),
        Div(
            A("Cancelar", href="/empleados", cls="btn btn-secondary"),
            Button("💾 Actualizar", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/empleados/actualizar"
    )

    contenido = Div(
        Div(
            Div(H2(f"✏️ Editar Empleado #{id_empleado}"),
                A("← Volver", href="/empleados", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Editar Empleado", f"✏️ {empleado['nombre']}", "", contenido)
