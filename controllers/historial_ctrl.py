"""
controllers/historial_ctrl.py
==============================
Controlador para el Historial de Mantenimiento.
"""
from controllers import deps
from auth import puede_acceder
from routes.historial import render_historial_list

def ctrl_historial_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "historial", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    
    historiales = deps.historial.listar()
    vehiculos = deps.vehiculos.listar()
    
    # Enriquecemos el historial con los datos del vehículo
    for h in historiales:
        v = next((v for v in vehiculos if v["id_vehiculo"] == h.get("idVehiculo")), None)
        h["vehiculo_str"] = f"{v['marca']} {v['modelo']} ({v['placa']})" if v else "Desconocido"

    return render_historial_list(req, historiales)
