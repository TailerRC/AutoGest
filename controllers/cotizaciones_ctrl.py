"""
controllers/cotizaciones_ctrl.py
=================================
Controlador para las Cotizaciones.
"""
import json
from fasthtml.common import RedirectResponse
from controllers import deps
from auth import puede_acceder, registrar_accion
from routes.cotizaciones import (
    render_cotizaciones_list,
    render_cotizaciones_nueva,
    render_cotizaciones_detalle,
)


def ctrl_cotizaciones_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "cotizaciones", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)

    cotizaciones = deps.cotizaciones.listar()
    clientes = deps.clientes.listar()
    vehiculos = deps.vehiculos.listar()

    for c in cotizaciones:
        cli = next((cl for cl in clientes if cl["id_cliente"] == c.get("idCliente")), None)
        veh = next((v for v in vehiculos if v["id_vehiculo"] == c.get("idVehiculo")), None)
        c["cliente_str"] = cli["nombre"] if cli else "Desconocido"
        c["vehiculo_str"] = f"{veh['marca']} {veh['modelo']} ({veh['placa']})" if veh else "Desconocido"

        # Calcular estado de vigencia
        from datetime import date
        try:
            fecha_v = date.fromisoformat(str(c.get("fecha_validez", "2000-01-01"))[:10])
            c["vigente"] = fecha_v >= date.today()
        except Exception:
            c["vigente"] = False

    return render_cotizaciones_list(req, usuario, cotizaciones)


def ctrl_cotizaciones_nueva(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "cotizaciones", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    clientes = deps.clientes.listar()
    vehiculos = deps.vehiculos.listar()
    return render_cotizaciones_nueva(req, clientes, vehiculos)


def ctrl_cotizaciones_crear(req, id_cliente: int, id_vehiculo: int,
                            fecha_validez: str, items_json: str, total: float):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "cotizaciones", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        servicios = json.loads(items_json) if items_json else []
        deps.cotizaciones.crear(id_cliente, id_vehiculo, fecha_validez, servicios, total)
        registrar_accion(usuario, "CREAR", "cotizaciones")
        return RedirectResponse("/cotizaciones?msg=creado", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/cotizaciones/nueva?error={str(e)}", status_code=303)


def ctrl_cotizaciones_detalle(req, codigo: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "cotizaciones", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    cot = deps.cotizaciones.obtener_por_codigo(codigo)
    clientes = deps.clientes.listar()
    vehiculos = deps.vehiculos.listar()
    if cot:
        cli = next((c for c in clientes if c["id_cliente"] == cot.get("idCliente")), None)
        veh = next((v for v in vehiculos if v["id_vehiculo"] == cot.get("idVehiculo")), None)
        cot["cliente_str"] = cli["nombre"] if cli else "—"
        cot["vehiculo_str"] = f"{veh['marca']} {veh['modelo']} ({veh['placa']})" if veh else "—"
    return render_cotizaciones_detalle(req, cot)
