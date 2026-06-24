"""
controllers/repuestos_ctrl.py
==============================
Controller de Repuestos / Inventario.
"""
from fasthtml.common import RedirectResponse
from auth import puede_acceder, registrar_accion
from controllers import deps
from routes.repuestos import (
    render_repuestos_list,
    render_repuestos_nuevo,
    render_repuestos_editar,
)


def ctrl_repuestos_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    repuestos = deps.repuestos.listar()
    return render_repuestos_list(req, usuario, repuestos)


def ctrl_repuestos_nuevo(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    return render_repuestos_nuevo(req)


def ctrl_repuestos_crear(req, codigo: str, nombre: str, stock: int,
                          precio_venta: float, proveedor: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.repuestos.crear(codigo, nombre, stock, precio_venta, proveedor)
        registrar_accion(usuario, "CREAR", "repuestos")
        return RedirectResponse("/repuestos?msg=creado", status_code=303)
    except ValueError as e:
        return RedirectResponse(f"/repuestos/nuevo?error={str(e)}", status_code=303)


def ctrl_repuestos_editar(req, id_pieza: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    repuesto = deps.repuestos.obtener(id_pieza)
    if not repuesto:
        return RedirectResponse("/repuestos", status_code=303)
    return render_repuestos_editar(req, repuesto)


def ctrl_repuestos_actualizar(req, id_pieza: int, codigo: str, nombre: str,
                               stock: int, precio_venta: float, proveedor: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    deps.repuestos.actualizar(id_pieza, codigo, nombre, stock, precio_venta, proveedor)
    registrar_accion(usuario, "EDITAR", "repuestos")
    return RedirectResponse("/repuestos?msg=editado", status_code=303)


def ctrl_repuestos_eliminar(req, id_pieza: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "eliminar"):
        from routes.helpers import no_perm
        return no_perm(req)
    deps.repuestos.eliminar(id_pieza)
    registrar_accion(usuario, "ELIMINAR", "repuestos")
    return RedirectResponse("/repuestos?msg=eliminado", status_code=303)
