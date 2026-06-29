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
    usuarios = deps.usuarios.listar()
    return render_reportes_list(req, ordenes, logs, resumen, mecanicos, usuarios=usuarios)


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

    id_vehiculo = datos["vehiculo"].get("id_vehiculo")
    todas_bitacoras = deps.bitacora.listar()
    bitacoras_vehiculo = [b for b in todas_bitacoras if b.get("idVehiculo") == id_vehiculo]
    datos["bitacoras_vehiculo"] = bitacoras_vehiculo

    vigentes = deps.cotizaciones.listar_vigentes_por_vehiculo(id_vehiculo) if id_vehiculo else []
    servicios_cotizacion = []
    if vigentes:
        repuestos_inventario = deps.repuestos.listar()
        clasificacion = deps.ordenes.clasificar_cotizacion(vigentes[0], repuestos_inventario)
        servicios_cotizacion = clasificacion["servicios"]
    datos["servicios_cotizacion"] = servicios_cotizacion

    return render_reportes_detalle(req, datos)
