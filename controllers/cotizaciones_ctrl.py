"""
controllers/cotizaciones_ctrl.py
=================================
Controlador para las Cotizaciones.
"""
from controllers import deps
from auth import puede_acceder
from routes.cotizaciones import render_cotizaciones_list

def ctrl_cotizaciones_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "cotizaciones", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    
    cotizaciones = deps.cotizaciones.listar()
    clientes = deps.clientes.listar()
    vehiculos = deps.vehiculos.listar()
    
    # Enriquecemos
    for c in cotizaciones:
        cli = next((cli for cli in clientes if cli["id_cliente"] == c.get("idCliente")), None)
        veh = next((veh for veh in vehiculos if veh["id_vehiculo"] == c.get("idVehiculo")), None)
        
        c["cliente_str"] = cli["nombre"] if cli else "Desconocido"
        c["vehiculo_str"] = f"{veh['marca']} {veh['modelo']}" if veh else "Desconocido"

    return render_cotizaciones_list(req, cotizaciones)
