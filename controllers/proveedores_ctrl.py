"""
controllers/proveedores_ctrl.py
================================
Controlador para los Proveedores.
"""
from controllers import deps
from auth import puede_acceder
from routes.proveedores import render_proveedores_list

def ctrl_proveedores_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "proveedores", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    
    proveedores = deps.proveedores.listar()
    return render_proveedores_list(req, proveedores)
