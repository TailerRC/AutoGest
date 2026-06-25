"""
controllers/proveedores_ctrl.py
================================
Controlador para los Proveedores.
"""
from fasthtml.common import RedirectResponse
from controllers import deps
from auth import puede_acceder, registrar_accion
from routes.proveedores import (
    render_proveedores_list,
    render_proveedores_nuevo,
    render_proveedores_editar,
)


def ctrl_proveedores_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "proveedores", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    proveedores = deps.proveedores.listar()
    return render_proveedores_list(req, usuario, proveedores)


def ctrl_proveedores_nuevo(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "proveedores", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    return render_proveedores_nuevo(req)


def ctrl_proveedores_crear(req, codigo: str, nombre_empresa: str,
                           lineas_raw: str, telefono: str, email: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "proveedores", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        lineas = [l.strip() for l in lineas_raw.split(",") if l.strip()]
        deps.proveedores.crear(codigo, nombre_empresa, lineas, telefono, email)
        registrar_accion(usuario, "CREAR", "proveedores")
        return RedirectResponse("/proveedores?msg=creado", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/proveedores/nuevo?error={str(e)}", status_code=303)


def ctrl_proveedores_editar(req, codigo: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "proveedores", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    proveedor = deps.proveedores.obtener_por_codigo(codigo)
    if not proveedor:
        return RedirectResponse("/proveedores", status_code=303)
    return render_proveedores_editar(req, proveedor)


def ctrl_proveedores_actualizar(req, codigo: str, nombre_empresa: str,
                                lineas_raw: str, telefono: str, email: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "proveedores", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        lineas = [l.strip() for l in lineas_raw.split(",") if l.strip()]
        deps.proveedores.actualizar(codigo, nombre_empresa, lineas, telefono, email)
        registrar_accion(usuario, "EDITAR", "proveedores")
        return RedirectResponse("/proveedores?msg=editado", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/proveedores/{codigo}/editar?error={str(e)}", status_code=303)
