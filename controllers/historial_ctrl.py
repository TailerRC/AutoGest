"""
controllers/historial_ctrl.py
==============================
Controlador para el Historial de Mantenimiento.
"""
from datetime import datetime, date
import urllib.parse
from fasthtml.common import RedirectResponse
from controllers import deps
from auth import puede_acceder, registrar_accion
from routes.historial import render_historial_list, render_historial_nuevo


def ctrl_historial_list(req):
    """
    Controlador para listar el historial de mantenimiento con filtros, ordenación y paginación.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "historial", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)

    # 1. Obtener parámetros del request
    q = req.query_params.get("q", "").strip().lower()
    estado = req.query_params.get("estado", "todos").strip().lower()
    orden = req.query_params.get("orden", "fecha_desc").strip()
    try:
        page = int(req.query_params.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    # 2. Consultar colecciones de MongoDB y Oracle
    historiales = deps.historial.listar()
    vehiculos = deps.vehiculos.listar()

    # 3. Enriquecer los registros NoSQL con los datos relacionales de Oracle y formatear fechas
    for h in historiales:
        v = next((v for v in vehiculos if v["id_vehiculo"] == h.get("idVehiculo")), None)
        h["vehiculo_str"] = f"{v['marca']} {v['modelo']} ({v['placa']})" if v else "Desconocido"
        h["placa"] = v["placa"] if v else "—"
        h["vehiculo_marca"] = v.get("marca", "") if v else ""
        h["vehiculo_modelo"] = v.get("modelo", "") if v else ""

        # Formatear la fecha de servicio de forma segura para búsqueda y renderizado
        fecha_val = h.get("fecha_servicio")
        if hasattr(fecha_val, "strftime"):
            h["fecha_servicio_str"] = fecha_val.strftime("%d/%m/%Y")
            h["fecha_servicio_iso"] = fecha_val.strftime("%Y-%m-%d")
        elif isinstance(fecha_val, str) and len(fecha_val) >= 10:
            try:
                dt = datetime.strptime(fecha_val[:10], "%Y-%m-%d")
                h["fecha_servicio_str"] = dt.strftime("%d/%m/%Y")
                h["fecha_servicio_iso"] = dt.strftime("%Y-%m-%d")
            except Exception:
                h["fecha_servicio_str"] = fecha_val
                h["fecha_servicio_iso"] = fecha_val[:10]
        else:
            h["fecha_servicio_str"] = str(fecha_val)
            h["fecha_servicio_iso"] = "2000-01-01"

    # 4. Filtrado en memoria (debido al cruce híbrido NoSQL + Relacional)
    filtered = []
    for h in historiales:
        # Búsqueda por vehículo, placa, diagnóstico, estado o fecha
        if q:
            match_vehiculo = q in h.get("vehiculo_str", "").lower()
            match_placa = q in h.get("placa", "").lower()
            match_diagnostico = any(q in d.lower() for d in h.get("diagnosticos_asociados", []))
            match_estado = q in h.get("estado_final", "").lower()
            match_fecha = q in h.get("fecha_servicio_str", "").lower()
            
            if not (match_vehiculo or match_placa or match_diagnostico or match_estado or match_fecha):
                continue

        # Filtro de estado
        if estado != "todos":
            if h.get("estado_final", "").lower() != estado:
                continue

        filtered.append(h)

    # 5. Ordenamiento en memoria
    def get_sort_key_fecha(x):
        return x.get("fecha_servicio_iso", "")

    def get_sort_key_km(x):
        try:
            return int(x.get("kilometraje_ingreso", 0))
        except (ValueError, TypeError):
            return 0

    if orden == "fecha_desc":
        filtered.sort(key=get_sort_key_fecha, reverse=True)
    elif orden == "fecha_asc":
        filtered.sort(key=get_sort_key_fecha, reverse=False)
    elif orden == "km_desc":
        filtered.sort(key=get_sort_key_km, reverse=True)
    elif orden == "km_asc":
        filtered.sort(key=get_sort_key_km, reverse=False)

    # 6. Paginación de resultados (6 por página)
    limit = 6
    total_count = len(filtered)
    total_pages = max(1, (total_count + limit - 1) // limit)

    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_historial = filtered[start_idx:end_idx]

    return render_historial_list(
        req, usuario, paginated_historial,
        q=q, estado=estado, orden=orden,
        page=page, total_pages=total_pages, total_count=total_count
    )


def ctrl_historial_nuevo(req):
    """
    Controlador para renderizar el formulario de nuevo registro de historial.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "historial", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    vehiculos = deps.vehiculos.listar()
    return render_historial_nuevo(req, vehiculos)


def ctrl_historial_crear(req, id_vehiculo: int, kilometraje_ingreso: int,
                         fecha_servicio: str, estado_final: str):
    """
    Controlador para procesar la creación de un registro de historial con validación de fecha.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "historial", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.historial.crear(id_vehiculo, kilometraje_ingreso, fecha_servicio, estado_final)
        registrar_accion(usuario, "CREAR", "historial")
        return RedirectResponse("/historial?msg=creado", status_code=303)
    except Exception as e:
        error_msg = urllib.parse.quote(str(e))
        return RedirectResponse(f"/historial/nuevo?error={error_msg}", status_code=303)

