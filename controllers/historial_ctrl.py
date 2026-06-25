"""
controllers/historial_ctrl.py
==============================
Controlador para el Historial de Mantenimiento.
"""
from fasthtml.common import RedirectResponse
from controllers import deps
from auth import puede_acceder, registrar_accion
from routes.historial import render_historial_list, render_historial_nuevo


def ctrl_historial_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "historial", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)

    historiales = deps.historial.listar()
    vehiculos = deps.vehiculos.listar()

    # Enriquecemos con datos Oracle
    for h in historiales:
        v = next((v for v in vehiculos if v["id_vehiculo"] == h.get("idVehiculo")), None)
        h["vehiculo_str"] = f"{v['marca']} {v['modelo']} ({v['placa']})" if v else "Desconocido"
        h["placa"] = v["placa"] if v else "—"

    return render_historial_list(req, usuario, historiales)


def ctrl_historial_nuevo(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "historial", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    vehiculos = deps.vehiculos.listar()
    return render_historial_nuevo(req, vehiculos)


def ctrl_historial_crear(req, id_vehiculo: int, kilometraje_ingreso: int,
                         fecha_servicio: str, estado_final: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "historial", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.historial.crear(id_vehiculo, kilometraje_ingreso, fecha_servicio, estado_final)
        registrar_accion(usuario, "CREAR", "historial")
        return RedirectResponse("/historial?msg=creado", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/historial/nuevo?error={str(e)}", status_code=303)
