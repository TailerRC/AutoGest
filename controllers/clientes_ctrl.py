"""
controllers/clientes_ctrl.py
=============================
Controller de Clientes.
Responsabilidad: validar sesión/permisos, extraer parámetros HTTP,
llamar al servicio y devolver la vista correcta.
"""
from fasthtml.common import RedirectResponse
from auth import puede_acceder, registrar_accion
from controllers import deps
from routes.clientes import (
    render_clientes_list,
    render_clientes_nuevo,
    render_clientes_editar,
)


def ctrl_clientes_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "clientes", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    
    page     = int(req.query_params.get("page", 1))
    per_page = int(req.query_params.get("per_page", 10))
    if per_page not in (10, 15, 20): per_page = 10
    if page < 1: page = 1

    todos    = deps.clientes.listar()
    total    = len(todos)
    inicio   = (page - 1) * per_page
    clientes = todos[inicio : inicio + per_page]

    return render_clientes_list(req, usuario, clientes, total, page, per_page)


def ctrl_clientes_nuevo(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "clientes", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    return render_clientes_nuevo(req)


def ctrl_clientes_crear(req, nombre: str, dni: str, telefono: str, email: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "clientes", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.clientes.crear(nombre, dni, telefono, email)
        registrar_accion(usuario, "CREAR", "clientes")
        return RedirectResponse("/clientes?msg=creado", status_code=303)
    except ValueError as e:
        return RedirectResponse(f"/clientes/nuevo?error={str(e)}", status_code=303)
    except Exception as e:
        if "ORA-00001" in str(e):
            msg = "Ya existe un cliente registrado con ese DNI o correo electrónico."
            return RedirectResponse(f"/clientes/nuevo?error={msg}", status_code=303)
        return RedirectResponse("/clientes/nuevo?error=Ocurrió un error inesperado.", status_code=303)


def ctrl_clientes_editar(req, id_cliente: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "clientes", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    cliente = deps.clientes.obtener(id_cliente)
    if not cliente:
        return RedirectResponse("/clientes", status_code=303)
    return render_clientes_editar(req, cliente)


def ctrl_clientes_actualizar(req, id_cliente: int, nombre: str,
                              dni: str, telefono: str, email: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "clientes", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.clientes.actualizar(id_cliente, nombre, dni, telefono, email)
        registrar_accion(usuario, "EDITAR", "clientes")
        return RedirectResponse("/clientes?msg=editado", status_code=303)
    except Exception as e:
        if "ORA-00001" in str(e):
            msg = "Ya existe otro cliente registrado con ese DNI o correo electrónico."
            return RedirectResponse(f"/clientes/{id_cliente}/editar?error={msg}", status_code=303)
        return RedirectResponse(f"/clientes/{id_cliente}/editar?error=Ocurrió un error inesperado.", status_code=303)

def ctrl_clientes_eliminar(req, id_cliente: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "clientes", "eliminar"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.clientes.eliminar(id_cliente)
        registrar_accion(usuario, "ELIMINAR", "clientes")
        return RedirectResponse("/clientes?msg=eliminado", status_code=303)
    except Exception as e:
        if "ORA-02292" in str(e):
            return RedirectResponse("/clientes?msg=con_vehiculos", status_code=303)
        return RedirectResponse("/clientes?msg=error", status_code=303)
