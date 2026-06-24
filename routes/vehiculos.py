"""
routes/vehiculos.py — View puro de Vehículos
=============================================
Solo renderiza HTML. Lógica en controllers/vehiculos_ctrl.py.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout

MARCAS = ["Toyota", "Hyundai", "Kia", "Nissan", "Chevrolet", "Honda", "Mazda",
          "Suzuki", "Mitsubishi", "Ford", "Volkswagen", "Renault"]


def render_vehiculos_list(req, usuario, vehiculos, clientes):
    """Renderiza la lista de vehículos."""
    msg = req.query_params.get("msg", "")
    alert_map = {
        "creado":    Div("✅ Vehículo registrado correctamente.", cls="alert alert-success"),
        "editado":   Div("✅ Vehículo actualizado.", cls="alert alert-success"),
        "eliminado": Div("🗑️ Vehículo eliminado.", cls="alert alert-warning"),
    }
    alert = alert_map.get(msg, "")

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
            Td(str(v.get("anio", v.get("año", "")))),
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


def render_vehiculos_nuevo(req, clientes):
    """Renderiza el formulario de nuevo vehículo."""
    opciones_clientes = [Option(f"{c['nombre']} (DNI: {c['dni']})", value=str(c["id_cliente"])) for c in clientes]

    form = Form(
        Div(
            Div(Label("Cliente propietario"),
                Select(Option("-- Seleccionar --", value=""), *opciones_clientes, name="id_cliente", required=True),
                cls="form-group"),
            Div(Label("Placa"), Input(name="placa", placeholder="ABC-123", required=True, maxlength="8"), cls="form-group"),
            Div(Label("Marca"),
                Select(*[Option(m, value=m) for m in MARCAS], name="marca", required=True),
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


def render_vehiculos_editar(req, vehiculo, clientes):
    """Renderiza el formulario de edición de un vehículo."""
    id_vehiculo = vehiculo["id_vehiculo"]
    opciones = [
        Option(f"{c['nombre']}", value=str(c["id_cliente"]),
               selected=(c["id_cliente"] == vehiculo["id_cliente"]))
        for c in clientes
    ]

    form = Form(
        Div(
            Div(Label("Cliente propietario"), Select(*opciones, name="id_cliente", required=True), cls="form-group"),
            Div(Label("Placa"), Input(name="placa", value=vehiculo["placa"], required=True), cls="form-group"),
            Div(Label("Marca"),
                Select(*[Option(m, value=m, selected=(m == vehiculo["marca"])) for m in MARCAS],
                       name="marca", required=True),
                cls="form-group"),
            Div(Label("Modelo"), Input(name="modelo", value=vehiculo["modelo"], required=True), cls="form-group"),
            Div(Label("Año"), Input(name="anio", type="number", value=str(vehiculo.get("anio", vehiculo.get("año", ""))),
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
            Div(H2(f"✏️ Editar Vehículo {vehiculo['placa']}"),
                A("← Volver", href="/vehiculos", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Editar Vehículo", f"✏️ {vehiculo['placa']}", "", contenido)
