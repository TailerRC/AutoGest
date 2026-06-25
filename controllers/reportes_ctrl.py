"""
controllers/reportes_ctrl.py
=============================
Controller de Reportes Combinados Oracle + MongoDB.
"""
from fasthtml.common import RedirectResponse
from auth import puede_acceder
from controllers import deps
from routes.reportes import render_reportes_list, render_reportes_detalle


def ctrl_reportes_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "reportes", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    ordenes   = deps.reportes.get_ordenes_lista()
    logs      = deps.reportes.get_logs_recientes(limit=10)
    resumen   = deps.reportes.resumen_general()
    
    from database import OracleDB
    db = OracleDB()
    mecanicos = db.get_reporte_mecanicos()
    
    return render_reportes_list(req, ordenes, logs, resumen, mecanicos)


def ctrl_reportes_detalle(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "reportes", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    id_orden_str = req.query_params.get("id_orden", "")
    if not id_orden_str.isdigit():
        return RedirectResponse("/reportes", status_code=303)

    datos = deps.reportes.reporte_por_orden(int(id_orden_str))
    if not datos:
        return RedirectResponse("/reportes", status_code=303)
    return render_reportes_detalle(req, datos)
