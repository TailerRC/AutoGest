"""
controllers/bitacora_ctrl.py
=============================
Controller de Bitácora.
"""
from fasthtml.common import RedirectResponse
from auth import puede_acceder, registrar_accion
from controllers import deps
from routes.bitacora import (
    render_bitacora_list,
    render_bitacora_detalle,
    render_bitacora_nueva,
)

def ctrl_bitacora_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "bitacora", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    bitacoras = deps.bitacora.listar()
    empleados = deps.empleados.listar()
    vehiculos = deps.vehiculos.listar()
    # Resolver nombre empleado y vehículo desde Oracle
    for b in bitacoras:
        emp = next((e for e in empleados if e["id_empleado"] == b.get("idEmpleado")), None)
        b["nombre_empleado"] = emp["nombre"] if emp else f"Empleado #{b.get('idEmpleado','?')}"
        veh = next((v for v in vehiculos if v["id_vehiculo"] == b.get("idVehiculo")), None)
        b["placa_vehiculo"] = veh["placa"] if veh else f"Vehículo #{b.get('idVehiculo','?')}"
    return render_bitacora_list(req, usuario, bitacoras)

def ctrl_bitacora_nueva(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "bitacora", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    vehiculos = deps.vehiculos.listar()
    empleados = deps.empleados.listar()
    return render_bitacora_nueva(req, vehiculos, empleados)

def ctrl_bitacora_crear(req, id_vehiculo: int, id_empleado: int, codigo_especificacion: str,
                        sintomas: str, codigos_obd: str, observaciones: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "bitacora", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.bitacora.crear(id_vehiculo, id_empleado, codigo_especificacion,
                            sintomas, codigos_obd, observaciones)
        registrar_accion(usuario, "CREAR", "bitacora")
        return RedirectResponse(f"/bitacora/{id_vehiculo}?msg=creado", status_code=303)
    except ValueError as e:
        return RedirectResponse(f"/bitacora/nueva?error={str(e)}", status_code=303)

def ctrl_bitacora_detalle(req, id_vehiculo: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "bitacora", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    bitacora = deps.bitacora.obtener_por_vehiculo(id_vehiculo)
    vehiculo = deps.vehiculos.obtener(id_vehiculo)
    return render_bitacora_detalle(req, bitacora, vehiculo)
