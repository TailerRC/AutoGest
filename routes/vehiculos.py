"""
routes/vehiculos.py — CRUD de Vehículos (Oracle simulado)
"""
from fasthtml.common import *
from database import get_oracle_connection
from auth import puede_acceder, registrar_accion
from .helpers import layout, no_perm, badge_estado


def vehiculos_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "vehiculos", "ver"):
        return no_perm(req)

    db = get_oracle_connection()
    vehiculos = db.get_all_vehiculos()

    msg = req.query_params.get("msg", "")
    alert = ""
    if msg == "creado":
        alert = Div("✅ Vehículo registrado correctamente.", cls="alert alert-success")
    elif msg == "editado":
        alert = Div("✅ Vehículo actualizado.", cls="alert alert-success")
    elif msg == "eliminado":
        alert = Div("🗑️ Vehículo eliminado.", cls="alert alert-warning")

    filas = []
    for v in vehiculos:
        acciones = []
        if puede_acceder(usuario, "vehiculos", "editar"):
            acciones.append(A("✏️", href=f"/vehiculos/{v['id_vehiculo']}/editar", cls="btn btn-sm btn-blue"))
        if puede_acceder(usuario, "vehiculos", "eliminar"):
            acciones.append(
                Form(
                    Input(type="hidden", name="id_vehiculo", value=str(v["id_vehiculo"])),
                    Button("🗑️", type="submit", cls="btn btn-sm btn-danger",
                           onclick="return confirm('¿Eliminar vehículo?')"),
                    method="post", action="/vehiculos/eliminar"
                )
            )
        filas.append(Tr(
            Td(Span(v["placa"], cls="badge badge-gray font-mono")),
            Td(f"{v['marca']} {v['modelo']}"),
            Td(str(v["año"])),
            Td(v["nombre_cliente"]),
            Td(Div(*acciones, cls="flex gap-1") if acciones else "—"),
        ))

    tabla = Div(
        Table(
            Thead(Tr(Th("Placa"), Th("Vehículo"), Th("Año"), Th("Propietario"), Th("Acciones"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("No hay vehículos.", colspan="5", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    crear_btn = A("＋ Nuevo Vehículo", href="/vehiculos/nuevo", cls="btn btn-primary") \
        if puede_acceder(usuario, "vehiculos", "crear") else ""

    contenido = Div(
        alert,
        Div(
            Div(H2("🚗 Vehículos"), cls="card-header"),
            Div(
                Div(Span(f"{len(vehiculos)} registros", cls="text-muted text-sm"), crear_btn,
                    cls="flex gap-2", style="justify-content:space-between;align-items:center;margin-bottom:1rem;"),
                tabla, cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Vehículos", "🚗 Gestión de Vehículos", "Base de datos Oracle", contenido)


def vehiculos_nuevo(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "vehiculos", "crear"):
        return no_perm(req)

    db = get_oracle_connection()
    clientes = db.get_all_clientes()
    opciones_clientes = [Option(f"{c['nombre']} (DNI: {c['dni']})", value=str(c["id_cliente"])) for c in clientes]
    marcas = ["Toyota", "Hyundai", "Kia", "Nissan", "Chevrolet", "Honda", "Mazda", "Suzuki",
              "Mitsubishi", "Ford", "Volkswagen", "Renault"]

    form = Form(
        Div(
            Div(Label("Cliente propietario"),
                Select(Option("-- Seleccionar --", value=""), *opciones_clientes, name="id_cliente", required=True),
                cls="form-group"),
            Div(Label("Placa"), Input(name="placa", placeholder="ABC-123", required=True, maxlength="8"), cls="form-group"),
            Div(Label("Marca"),
                Select(*[Option(m, value=m) for m in marcas], name="marca", required=True),
                cls="form-group"),
            Div(Label("Modelo"), Input(name="modelo", placeholder="Corolla, Accent, Rio...", required=True), cls="form-group"),
            Div(Label("Año"), Input(name="anio", type="number", min="1990", max="2026",
                                   placeholder="2022", required=True), cls="form-group"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/vehiculos", cls="btn btn-secondary"),
            Button("💾 Guardar Vehículo", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/vehiculos/crear"
    )

    contenido = Div(
        Div(
            Div(H2("🚗 Nuevo Vehículo"), A("← Volver", href="/vehiculos", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nuevo Vehículo", "🚗 Nuevo Vehículo", "Vincular a cliente Oracle", contenido)


def vehiculos_crear(req, id_cliente: int, placa: str, marca: str, modelo: str, anio: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "vehiculos", "crear"):
        return no_perm(req)
    db = get_oracle_connection()
    db.create_vehiculo(id_cliente, placa.strip(), marca.strip(), modelo.strip(), anio)
    registrar_accion(usuario, "CREAR", "vehiculos")
    return RedirectResponse("/vehiculos?msg=creado", status_code=303)


def vehiculos_editar(req, id_vehiculo: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "vehiculos", "editar"):
        return no_perm(req)

    db = get_oracle_connection()
    v = db.get_vehiculo(id_vehiculo)
    if not v:
        return RedirectResponse("/vehiculos", status_code=303)

    clientes = db.get_all_clientes()
    opciones = [
        Option(f"{c['nombre']}", value=str(c["id_cliente"]),
               selected=(c["id_cliente"] == v["id_cliente"]))
        for c in clientes
    ]
    marcas = ["Toyota", "Hyundai", "Kia", "Nissan", "Chevrolet", "Honda", "Mazda",
              "Suzuki", "Mitsubishi", "Ford", "Volkswagen", "Renault"]

    form = Form(
        Div(
            Div(Label("Cliente propietario"), Select(*opciones, name="id_cliente", required=True), cls="form-group"),
            Div(Label("Placa"), Input(name="placa", value=v["placa"], required=True), cls="form-group"),
            Div(Label("Marca"),
                Select(*[Option(m, value=m, selected=(m == v["marca"])) for m in marcas],
                       name="marca", required=True),
                cls="form-group"),
            Div(Label("Modelo"), Input(name="modelo", value=v["modelo"], required=True), cls="form-group"),
            Div(Label("Año"), Input(name="anio", type="number", value=str(v["año"]),
                                   min="1990", max="2026", required=True), cls="form-group"),
            cls="form-grid"
        ),
        Input(type="hidden", name="id_vehiculo", value=str(id_vehiculo)),
        Div(
            A("Cancelar", href="/vehiculos", cls="btn btn-secondary"),
            Button("💾 Actualizar", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/vehiculos/actualizar"
    )

    contenido = Div(
        Div(
            Div(H2(f"✏️ Editar Vehículo {v['placa']}"),
                A("← Volver", href="/vehiculos", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Editar Vehículo", f"✏️ {v['placa']}", "", contenido)


def vehiculos_actualizar(req, id_vehiculo: int, id_cliente: int, placa: str, marca: str, modelo: str, anio: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "vehiculos", "editar"):
        return no_perm(req)
    db = get_oracle_connection()
    db.update_vehiculo(id_vehiculo, id_cliente, placa.strip(), marca.strip(), modelo.strip(), anio)
    registrar_accion(usuario, "EDITAR", "vehiculos")
    return RedirectResponse("/vehiculos?msg=editado", status_code=303)


def vehiculos_eliminar(req, id_vehiculo: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "vehiculos", "eliminar"):
        return no_perm(req)
    db = get_oracle_connection()
    db.delete_vehiculo(id_vehiculo)
    registrar_accion(usuario, "ELIMINAR", "vehiculos")
    return RedirectResponse("/vehiculos?msg=eliminado", status_code=303)
