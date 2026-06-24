"""
controllers/usuarios_ctrl.py
=============================
Controller de Usuarios (solo admin).
"""
from fasthtml.common import RedirectResponse
from auth import puede_acceder, registrar_accion
from controllers import deps
from routes.usuarios import (
    render_usuarios_list,
    render_usuarios_nuevo,
    render_usuarios_editar,
)


def ctrl_usuarios_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "usuarios", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    usuarios  = deps.usuarios.listar()
    empleados = deps.empleados.listar()
    return render_usuarios_list(req, usuario, usuarios)


def ctrl_usuarios_nuevo(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "usuarios", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    empleados = deps.empleados.listar()
    return render_usuarios_nuevo(req, empleados)


def ctrl_usuarios_crear(req, id_empleado: int, username: str,
                         password: str, rol: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "usuarios", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.usuarios.crear(id_empleado, username, password, rol)
        registrar_accion(usuario, "CREAR", "usuarios")
        return RedirectResponse("/usuarios?msg=creado", status_code=303)
    except ValueError as e:
        return RedirectResponse(f"/usuarios/nuevo?error={str(e)}", status_code=303)


def ctrl_usuarios_editar(req, id_usuario: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "usuarios", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    u = deps.usuarios.obtener(id_usuario)
    if not u:
        return RedirectResponse("/usuarios", status_code=303)
    empleados = deps.empleados.listar()
    return render_usuarios_editar(req, u, empleados)


def ctrl_usuarios_actualizar(req, id_usuario: int, id_empleado: int,
                              username: str, password: str, rol: str, estado: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "usuarios", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.usuarios.actualizar(id_usuario, id_empleado, username, password, rol, estado)
        registrar_accion(usuario, "EDITAR", "usuarios")
        return RedirectResponse("/usuarios?msg=editado", status_code=303)
    except ValueError as e:
        return RedirectResponse(f"/usuarios/{id_usuario}/editar?error={str(e)}", status_code=303)


def ctrl_usuarios_desactivar(req, id_usuario: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "usuarios", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    deps.usuarios.desactivar(id_usuario)
    registrar_accion(usuario, "DESACTIVAR", "usuarios")
    return RedirectResponse("/usuarios?msg=desactivado", status_code=303)
