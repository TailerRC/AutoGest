"""
controllers/empleados_ctrl.py
==============================
Controller de Empleados.
"""
from fasthtml.common import RedirectResponse
from auth import puede_acceder, registrar_accion
from controllers import deps
from routes.empleados import (
    render_empleados_list,
    render_empleados_nuevo,
    render_empleados_editar,
)


def ctrl_empleados_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "empleados", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    empleados = deps.empleados.listar()
    return render_empleados_list(req, usuario, empleados)


def ctrl_empleados_nuevo(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "empleados", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    return render_empleados_nuevo(req)


def ctrl_empleados_crear(req, nombre: str, cargo: str, especialidad: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "empleados", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.empleados.crear(nombre, cargo, especialidad)
        registrar_accion(usuario, "CREAR", "empleados")
        return RedirectResponse("/empleados?msg=creado", status_code=303)
    except ValueError as e:
        return RedirectResponse(f"/empleados/nuevo?error={str(e)}", status_code=303)


def ctrl_empleados_editar(req, id_empleado: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "empleados", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    empleado = deps.empleados.obtener(id_empleado)
    if not empleado:
        return RedirectResponse("/empleados", status_code=303)
    return render_empleados_editar(req, empleado)


def ctrl_empleados_actualizar(req, id_empleado: int,
                               nombre: str, cargo: str, especialidad: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "empleados", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    deps.empleados.actualizar(id_empleado, nombre, cargo, especialidad)
    registrar_accion(usuario, "EDITAR", "empleados")
    return RedirectResponse("/empleados?msg=editado", status_code=303)
