"""
controllers/facturas_ctrl.py
=============================
Controller de Facturas.
"""
from fasthtml.common import RedirectResponse
from auth import puede_acceder, registrar_accion
from controllers import deps
from routes.facturas import (
    render_facturas_list,
    render_facturas_nueva,
    render_facturas_detalle,
)


def ctrl_facturas_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "facturas", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    facturas = deps.facturas.listar()
    return render_facturas_list(req, usuario, facturas)


def ctrl_facturas_nueva(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "facturas", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    ordenes = deps.ordenes.listar()
    return render_facturas_nueva(req, ordenes)


def ctrl_facturas_crear(req, id_orden: int, total: float, metodo_pago: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "facturas", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.facturas.crear(id_orden, total, metodo_pago)
        registrar_accion(usuario, "CREAR", "facturas")
        return RedirectResponse("/facturas?msg=creado", status_code=303)
    except ValueError as e:
        return RedirectResponse(f"/facturas/nueva?error={str(e)}", status_code=303)


def ctrl_facturas_detalle(req, id_factura: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "facturas", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    factura = deps.facturas.obtener(id_factura)
    if not factura:
        return RedirectResponse("/facturas", status_code=303)
    return render_facturas_detalle(req, factura)


def ctrl_facturas_cambiar_estado(req, id_factura: int, estado_pago: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "facturas", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.facturas.cambiar_estado(id_factura, estado_pago)
        registrar_accion(usuario, "CAMBIAR_ESTADO", "facturas")
        return RedirectResponse(f"/facturas/{id_factura}?msg=actualizado", status_code=303)
    except ValueError as e:
        return RedirectResponse(f"/facturas/{id_factura}?error={str(e)}", status_code=303)
