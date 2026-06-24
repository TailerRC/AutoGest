"""
controllers/vehiculos_ctrl.py
==============================
Controller de Vehículos.
"""
from fasthtml.common import RedirectResponse
from auth import puede_acceder, registrar_accion
from controllers import deps
from routes.vehiculos import (
    render_vehiculos_list,
    render_vehiculos_nuevo,
    render_vehiculos_editar,
)


def ctrl_vehiculos_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "vehiculos", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    vehiculos = deps.vehiculos.listar()
    clientes  = deps.clientes.listar()
    return render_vehiculos_list(req, usuario, vehiculos, clientes)


def ctrl_vehiculos_nuevo(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "vehiculos", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    clientes = deps.clientes.listar()
    return render_vehiculos_nuevo(req, clientes)


def ctrl_vehiculos_crear(req, id_cliente: int, placa: str,
                          marca: str, modelo: str, anio: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "vehiculos", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.vehiculos.crear(id_cliente, placa, marca, modelo, anio)
        registrar_accion(usuario, "CREAR", "vehiculos")
        return RedirectResponse("/vehiculos?msg=creado", status_code=303)
    except ValueError as e:
        return RedirectResponse(f"/vehiculos/nuevo?error={str(e)}", status_code=303)


def ctrl_vehiculos_editar(req, id_vehiculo: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "vehiculos", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    vehiculo = deps.vehiculos.obtener(id_vehiculo)
    if not vehiculo:
        return RedirectResponse("/vehiculos", status_code=303)
    clientes = deps.clientes.listar()
    return render_vehiculos_editar(req, vehiculo, clientes)


def ctrl_vehiculos_actualizar(req, id_vehiculo: int, id_cliente: int,
                               placa: str, marca: str, modelo: str, anio: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "vehiculos", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    deps.vehiculos.actualizar(id_vehiculo, id_cliente, placa, marca, modelo, anio)
    registrar_accion(usuario, "EDITAR", "vehiculos")
    return RedirectResponse("/vehiculos?msg=editado", status_code=303)


def ctrl_vehiculos_eliminar(req, id_vehiculo: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "vehiculos", "eliminar"):
        from routes.helpers import no_perm
        return no_perm(req)
    deps.vehiculos.eliminar(id_vehiculo)
    registrar_accion(usuario, "ELIMINAR", "vehiculos")
    return RedirectResponse("/vehiculos?msg=eliminado", status_code=303)
