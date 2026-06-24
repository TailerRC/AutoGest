"""
controllers/catalogo_ctrl.py
=============================
Controller del Catálogo Técnico (MongoDB).
"""
from auth import puede_acceder
from controllers import deps
from routes.catalogo_tecnico import render_catalogo_list


def ctrl_catalogo_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "catalogo", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    marca  = req.query_params.get("marca", "")
    modelo = req.query_params.get("modelo", "")
    año_s  = req.query_params.get("año", "")
    año    = int(año_s) if año_s.isdigit() else None

    if marca or modelo or año:
        catalogo = deps.catalogo.buscar(marca=marca, modelo=modelo, año=año)
    else:
        catalogo = deps.catalogo.listar()

    return render_catalogo_list(req, catalogo)
