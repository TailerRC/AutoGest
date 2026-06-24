"""
controllers/ordenes_ctrl.py
============================
Controller de Órdenes de Trabajo.
"""
from fasthtml.common import RedirectResponse
from auth import puede_acceder, registrar_accion
from controllers import deps
from routes.ordenes import (
    render_ordenes_list,
    render_ordenes_detalle,
    render_ordenes_nueva,
    render_ordenes_editar,
)


def ctrl_ordenes_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    ordenes = deps.ordenes.listar()
    return render_ordenes_list(req, usuario, ordenes)


def ctrl_ordenes_detalle(req, id_orden: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    orden = deps.ordenes.obtener_detallada(id_orden)
    if not orden:
        return RedirectResponse("/ordenes", status_code=303)
    repuestos = deps.repuestos.listar()
    return render_ordenes_detalle(req, usuario, orden, repuestos)


def ctrl_ordenes_nueva(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    vehiculos = deps.vehiculos.listar()
    mecanicos = deps.empleados.listar_mecanicos()
    return render_ordenes_nueva(req, vehiculos, mecanicos)


def ctrl_ordenes_crear(req, id_vehiculo: int, id_empleado: int,
                        fecha_ingreso: str, fecha_entrega: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    nueva = deps.ordenes.crear(id_vehiculo, id_empleado, fecha_ingreso, fecha_entrega)
    registrar_accion(usuario, "CREAR", "ordenes")
    return RedirectResponse(f"/ordenes/{nueva['id_orden']}?msg=creado", status_code=303)


def ctrl_ordenes_editar(req, id_orden: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    orden = deps.ordenes.obtener(id_orden)
    if not orden:
        return RedirectResponse("/ordenes", status_code=303)
    vehiculos = deps.vehiculos.listar()
    empleados = deps.empleados.listar()
    return render_ordenes_editar(req, orden, vehiculos, empleados)


def ctrl_ordenes_actualizar(req, id_orden: int, id_vehiculo: int,
                             id_empleado: int, fecha_ingreso: str,
                             fecha_entrega: str, estado: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    deps.ordenes.actualizar(id_orden, id_vehiculo, id_empleado,
                             fecha_ingreso, fecha_entrega, estado)
    registrar_accion(usuario, "EDITAR", "ordenes")
    return RedirectResponse(f"/ordenes/{id_orden}?msg=actualizado", status_code=303)


def ctrl_ordenes_cambiar_estado(req, id_orden: int, estado: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    deps.ordenes.cambiar_estado(id_orden, estado)
    registrar_accion(usuario, "CAMBIAR_ESTADO", "ordenes")
    return RedirectResponse(f"/ordenes/{id_orden}?msg=actualizado", status_code=303)


def ctrl_ordenes_agregar_repuesto(req, id_orden: int, id_pieza: int,
                                   cantidad: int, precio_unitario: float):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.ordenes.agregar_repuesto(id_orden, id_pieza, cantidad, precio_unitario)
        registrar_accion(usuario, "AGREGAR_REPUESTO", "ordenes")
        return RedirectResponse(f"/ordenes/{id_orden}?msg=detalle_agregado", status_code=303)
    except ValueError as e:
        return RedirectResponse(f"/ordenes/{id_orden}?error={str(e)}", status_code=303)
