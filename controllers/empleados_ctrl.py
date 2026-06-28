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

    page     = int(req.query_params.get("page", 1))
    per_page = int(req.query_params.get("per_page", 10))
    buscar   = req.query_params.get("buscar", "").strip().lower()
    if per_page not in (10, 15, 20): per_page = 10
    if page < 1: page = 1

    todos = deps.empleados.listar()

    if buscar:
        todos = [e for e in todos if buscar in e["cargo"].lower()]

    total     = len(todos)
    inicio    = (page - 1) * per_page
    empleados = todos[inicio : inicio + per_page]

    return render_empleados_list(req, usuario, empleados, total, page, per_page, buscar)

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

def ctrl_empleados_eliminar(req, id_empleado: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "empleados", "eliminar"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.empleados.eliminar(id_empleado)
        registrar_accion(usuario, "ELIMINAR", "empleados")
        return RedirectResponse("/empleados?msg=eliminado", status_code=303)
    except Exception as e:
        if "ORA-02292" in str(e):
            return RedirectResponse("/empleados?msg=con_ordenes", status_code=303)
        return RedirectResponse("/empleados?msg=error", status_code=303)