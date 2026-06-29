"""
controllers/cotizaciones_ctrl.py
=================================
Controlador para las Cotizaciones.
"""
import json
from datetime import datetime, date
from fasthtml.common import RedirectResponse
from controllers import deps
from auth import puede_acceder, registrar_accion
from routes.cotizaciones import (
    render_cotizaciones_list,
    render_cotizaciones_nueva,
    render_cotizaciones_detalle,
)


def ctrl_cotizaciones_list(req):
    """
    Controlador para listar cotizaciones con búsqueda, filtros, ordenamiento y paginación.
    
    Propósito:
      - Extraer parámetros de búsqueda del request.
      - Resolver las referencias relacionales de Oracle (Cliente, Vehículo).
      - Aplicar filtros lógicos en memoria para búsquedas cruzadas NoSQL + Relacional.
      - Ordenar y paginar el set de resultados antes de renderizar la vista.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "cotizaciones", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)

    # 1. Obtener parámetros de consulta para búsqueda y paginación
    q = req.query_params.get("q", "").strip().lower()
    estado = req.query_params.get("estado", "todos")
    orden = req.query_params.get("orden", "fecha_desc")
    try:
        page = int(req.query_params.get("page", 1))
        if page < 1: page = 1
    except ValueError:
        page = 1

    # 2. Obtener datos de MongoDB y Oracle
    cotizaciones = deps.cotizaciones.listar()
    clientes = deps.clientes.listar()
    vehiculos = deps.vehiculos.listar()

    # 3. Cruzar datos relacionales y calcular vigencia
    for c in cotizaciones:
        cli = next((cl for cl in clientes if cl["id_cliente"] == c.get("idCliente")), None)
        veh = next((v for v in vehiculos if v["id_vehiculo"] == c.get("idVehiculo")), None)
        c["cliente_str"] = cli["nombre"] if cli else "Desconocido"
        c["vehiculo_str"] = f"{veh['marca']} {veh['modelo']} ({veh['placa']})" if veh else "Desconocido"
        c["vehiculo_placa"] = veh["placa"] if veh else ""
        c["vehiculo_marca"] = veh.get("marca", "") if veh else ""
        c["vehiculo_modelo"] = veh.get("modelo", "") if veh else ""

        # Formatear la fecha de validez de manera segura
        fecha_val = c.get("fecha_validez")
        if hasattr(fecha_val, "strftime"):
            c["fecha_validez_str"] = fecha_val.strftime("%Y-%m-%d")
            fecha_v_date = fecha_val.date()
        else:
            fecha_str = str(fecha_val)[:10] if fecha_val else "2000-01-01"
            c["fecha_validez_str"] = fecha_str
            try:
                fecha_v_date = date.fromisoformat(fecha_str)
            except Exception:
                fecha_v_date = date(2000, 1, 1)

        c["vigente"] = fecha_v_date >= date.today()

    # 4. Aplicar Búsqueda y Filtros en memoria (debido al cruce híbrido NoSQL + Relacional)
    filtered = []
    for c in cotizaciones:
        # Filtro de búsqueda
        if q:
            match_codigo = q in c.get("codigoCotizacion", "").lower()
            match_cliente = q in c.get("cliente_str", "").lower()
            match_placa = q in c.get("vehiculo_placa", "").lower()
            match_marca = q in c.get("vehiculo_marca", "").lower()
            match_modelo = q in c.get("vehiculo_modelo", "").lower()
            if not (match_codigo or match_cliente or match_placa or match_marca or match_modelo):
                continue

        # Filtro de vigencia
        if estado == "vigente" and not c["vigente"]:
            continue
        if estado == "vencida" and c["vigente"]:
            continue

        filtered.append(c)

    # 5. Ordenamiento robusto de tipos mixtos (BSON datetime / Strings / Floats)
    def get_sort_key(c, field):
        if field == "fecha":
            val = c.get("fecha_validez")
            if not val:
                return ""
            if hasattr(val, "isoformat"):
                return val.isoformat()
            return str(val)
        elif field == "total":
            try:
                return float(c.get("total", 0.0))
            except (ValueError, TypeError):
                return 0.0
        return ""

    if orden == "fecha_desc":
        filtered.sort(key=lambda x: get_sort_key(x, "fecha"), reverse=True)
    elif orden == "fecha_asc":
        filtered.sort(key=lambda x: get_sort_key(x, "fecha"), reverse=False)
    elif orden == "total_desc":
        filtered.sort(key=lambda x: get_sort_key(x, "total"), reverse=True)
    elif orden == "total_asc":
        filtered.sort(key=lambda x: get_sort_key(x, "total"), reverse=False)

    # 6. Paginación de resultados (6 por página)
    limit = 6
    total_count = len(filtered)
    total_pages = max(1, (total_count + limit - 1) // limit)
    
    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_cotizaciones = filtered[start_idx:end_idx]

    return render_cotizaciones_list(
        req, usuario, paginated_cotizaciones, 
        q=q, estado=estado, orden=orden, 
        page=page, total_pages=total_pages, total_count=total_count
    )


def ctrl_cotizaciones_nueva(req):
    """
    Controlador para mostrar la pantalla de registro de nueva cotización.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "cotizaciones", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    clientes = deps.clientes.listar()
    vehiculos = deps.vehiculos.listar()
    repuestos = deps.repuestos.listar()
    bitacoras = deps.bitacora.listar()

    # VW_VEHICULOS no expone id_cliente (solo nombre_cliente), así que lo
    # reconstruimos consultando cada vehículo individualmente (get_by_id sí
    # devuelve id_cliente, según VEHICULOS directo en database.py).
    for v in vehiculos:
        if "id_cliente" not in v:
            detalle = deps.vehiculos.obtener(v["id_vehiculo"])
            v["id_cliente"] = detalle["id_cliente"] if detalle else None

    return render_cotizaciones_nueva(req, clientes, vehiculos, repuestos, bitacoras)


def ctrl_cotizaciones_crear(req, id_cliente: int, id_vehiculo: int,
                             fecha_validez: str, items_json: str, total: float):
    """
    Controlador para procesar la creación de una cotización con servicios embebidos.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "cotizaciones", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        # Deserializar los ítems dinámicos enviados del cliente
        servicios = json.loads(items_json) if items_json else []
        
        # Invocar la capa de servicio para validación y persistencia
        deps.cotizaciones.crear(id_cliente, id_vehiculo, fecha_validez, servicios, total)
        
        # Registrar log administrativo de auditoría
        registrar_accion(usuario, "CREAR", "cotizaciones")
        return RedirectResponse("/cotizaciones?msg=creado", status_code=303)
    except Exception as e:
        # En caso de error, volver al formulario y mostrar la excepción descriptiva
        return RedirectResponse(f"/cotizaciones/nueva?error={str(e)}", status_code=303)


def ctrl_cotizaciones_detalle(req, codigo: str):
    """
    Controlador para visualizar el detalle individual de una cotización NoSQL.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "cotizaciones", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    
    cot = deps.cotizaciones.obtener_por_codigo(codigo)
    clientes = deps.clientes.listar()
    vehiculos = deps.vehiculos.listar()
    
    if cot:
        # Resolver strings de Cliente y Vehículo desde la BD Oracle
        cli = next((c for c in clientes if c["id_cliente"] == cot.get("idCliente")), None)
        veh = next((v for v in vehiculos if v["id_vehiculo"] == cot.get("idVehiculo")), None)
        cot["cliente_str"] = cli["nombre"] if cli else "Desconocido"
        cot["vehiculo_str"] = f"{veh['marca']} {veh['modelo']} ({veh['placa']})" if veh else "Desconocido"

        # Formatear la fecha para visualización en detalle
        fecha_val = cot.get("fecha_validez")
        if hasattr(fecha_val, "strftime"):
            cot["fecha_validez_str"] = fecha_val.strftime("%Y-%m-%d")
        else:
            cot["fecha_validez_str"] = str(fecha_val)[:10] if fecha_val else "—"

    return render_cotizaciones_detalle(req, cot)
