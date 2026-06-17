"""
routes/empleados.py — CRUD de Empleados (Oracle simulado)
"""
from fasthtml.common import *
from database import get_oracle_connection
from auth import puede_acceder, registrar_accion
from .helpers import layout, no_perm


ESPECIALIDADES = [
    "Mecánica General", "Motor y Transmisión", "Electricidad Automotriz",
    "Frenos y Suspensión", "Carrocería y Pintura", "Gestión y Facturación",
    "Diagnóstico Electrónico", "Aire Acondicionado Automotriz"
]

CARGOS = [
    "Jefe de Taller", "Mecánico Senior", "Mecánico", "Electricista Automotriz",
    "Asistente Administrativo", "Asesor de Ventas", "Recepcionista"
]


def empleados_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "empleados", "ver"):
        return no_perm(req)

    db = get_oracle_connection()
    empleados = db.get_all_empleados()

    msg = req.query_params.get("msg", "")
    alert = ""
    if msg == "creado":
        alert = Div("✅ Empleado registrado.", cls="alert alert-success")
    elif msg == "editado":
        alert = Div("✅ Empleado actualizado.", cls="alert alert-success")

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


def empleados_nuevo(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "empleados", "crear"):
        return no_perm(req)

    form = Form(
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


def empleados_crear(req, nombre: str, cargo: str, especialidad: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "empleados", "crear"):
        return no_perm(req)
    db = get_oracle_connection()
    db.create_empleado(nombre.strip(), cargo.strip(), especialidad.strip())
    registrar_accion(usuario, "CREAR", "empleados")
    return RedirectResponse("/empleados?msg=creado", status_code=303)


def empleados_editar(req, id_empleado: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "empleados", "editar"):
        return no_perm(req)

    db = get_oracle_connection()
    e = db.get_empleado(id_empleado)
    if not e:
        return RedirectResponse("/empleados", status_code=303)

    form = Form(
        Div(
            Div(Label("Nombre completo"), Input(name="nombre", value=e["nombre"], required=True), cls="form-group"),
            Div(Label("Cargo"),
                Select(*[Option(c, value=c, selected=(c == e["cargo"])) for c in CARGOS],
                       name="cargo", required=True),
                cls="form-group"),
            Div(Label("Especialidad"),
                Select(*[Option(es, value=es, selected=(es == e["especialidad"])) for es in ESPECIALIDADES],
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
    return layout(req, "Editar Empleado", f"✏️ {e['nombre']}", "", contenido)


def empleados_actualizar(req, id_empleado: int, nombre: str, cargo: str, especialidad: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "empleados", "editar"):
        return no_perm(req)
    db = get_oracle_connection()
    db.update_empleado(id_empleado, nombre.strip(), cargo.strip(), especialidad.strip())
    registrar_accion(usuario, "EDITAR", "empleados")
    return RedirectResponse("/empleados?msg=editado", status_code=303)
