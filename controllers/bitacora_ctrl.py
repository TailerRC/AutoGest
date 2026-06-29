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

    q = req.query_params.get("q", "").strip().lower()
    try:
        page = int(req.query_params.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    bitacoras = deps.bitacora.listar()
    empleados = deps.empleados.listar()
    vehiculos = deps.vehiculos.listar()
    # Resolver nombre empleado y vehículo desde Oracle
    for b in bitacoras:
        emp = next((e for e in empleados if e["id_empleado"] == b.get("idEmpleado")), None)
        b["nombre_empleado"] = emp["nombre"] if emp else f"Empleado #{b.get('idEmpleado','?')}"
        veh = next((v for v in vehiculos if v["id_vehiculo"] == b.get("idVehiculo")), None)
        b["placa_vehiculo"] = veh["placa"] if veh else f"Vehículo #{b.get('idVehiculo','?')}"

    # Búsqueda por placa, código de diagnóstico, o nombre de mecánico
    if q:
        bitacoras = [
            b for b in bitacoras
            if q in b.get("placa_vehiculo", "").lower()
            or q in b.get("codigoDiagnostico", "").lower()
            or q in b.get("nombre_empleado", "").lower()
        ]

    # Paginación (6 por página, mismo patrón que Repuestos/Cotizaciones/Órdenes)
    limit = 6
    total_count = len(bitacoras)
    total_pages = max(1, (total_count + limit - 1) // limit)
    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    bitacoras_pag = bitacoras[start_idx:end_idx]

    return render_bitacora_list(
        req, usuario, bitacoras_pag,
        q=q, page=page, total_pages=total_pages, total_count=total_count
    )

def ctrl_bitacora_nueva(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "bitacora", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    vehiculos = deps.vehiculos.listar()
    empleados = deps.empleados.listar()
    catalogo = deps.catalogo.listar()
    return render_bitacora_nueva(req, vehiculos, empleados, catalogo)

def ctrl_bitacora_crear(req, id_vehiculo: int, id_empleado: int, codigo_especificacion: str,
                        sintomas: str, codigos_obd: str, observaciones: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "bitacora", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        nueva = deps.bitacora.crear(id_vehiculo, id_empleado, codigo_especificacion,
                                     sintomas, codigos_obd, observaciones)
        registrar_accion(usuario, "CREAR", "bitacora")
        return RedirectResponse(f"/bitacora/diagnostico/{nueva['codigoDiagnostico']}?msg=creado", status_code=303)
    except ValueError as e:
        import urllib.parse
        error_msg = urllib.parse.quote(str(e))
        return RedirectResponse(f"/bitacora/nueva?error={error_msg}", status_code=303)
    except Exception as e:
        import urllib.parse
        error_msg = urllib.parse.quote(f"Error al guardar en MongoDB: {str(e)}")
        return RedirectResponse(f"/bitacora/nueva?error={error_msg}", status_code=303)

async def ctrl_bitacora_subir_fotos(req, codigo_diagnostico: str):
    """
    Sube las 3 fotos de evidencia (frontal, lateral, angular) de una bitácora
    ya creada. La carpeta se nombra {PLACA}-{codigoDiagnostico}, y las rutas
    resultantes se agregan al array fotografias_url del documento en Mongo.
    """
    import os

    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "bitacora", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)

    bitacora = deps.bitacora.obtener_por_codigo(codigo_diagnostico)
    if not bitacora:
        return RedirectResponse("/bitacora?error=Bitácora+no+encontrada", status_code=303)
    vehiculo = deps.vehiculos.obtener(bitacora.get("idVehiculo"))
    if not vehiculo:
        return RedirectResponse(f"/bitacora/diagnostico/{codigo_diagnostico}?error=Vehículo+no+encontrado", status_code=303)

    form = await req.form()
    placa = vehiculo["placa"].upper().strip()

    archivos = {
        "FRONTAL": form.get("foto_frontal"),
        "LATERAL": form.get("foto_lateral"),
        "ANGULAR": form.get("foto_angular"),
    }

    for vista, archivo in archivos.items():
        if not archivo or not getattr(archivo, "filename", None):
            return RedirectResponse(
                f"/bitacora/diagnostico/{codigo_diagnostico}?error=Debes+subir+las+3+fotos+({vista}+falta)",
                status_code=303
            )

    FOTOS_PATH = os.getenv("FOTOS_VEHICULOS_PATH", "fotos_vehiculos")
    carpeta_nombre = f"{placa}-{codigo_diagnostico}"
    carpeta = os.path.join(FOTOS_PATH, carpeta_nombre)
    os.makedirs(carpeta, exist_ok=True)

    urls_guardadas = []
    for vista, archivo in archivos.items():
        ext = os.path.splitext(archivo.filename)[1].lower() or ".jpg"
        nombre = f"{carpeta_nombre}_{vista}{ext}"
        destino = os.path.join(carpeta, nombre)
        contenido = await archivo.read()
        with open(destino, "wb") as f:
            f.write(contenido)
        urls_guardadas.append(f"{carpeta_nombre}/{nombre}")

    try:
        deps.bitacora.agregar_fotos(codigo_diagnostico, urls_guardadas)
        registrar_accion(usuario, "SUBIR_FOTOS", "bitacora")
        return RedirectResponse(f"/bitacora/diagnostico/{codigo_diagnostico}?msg=fotos_ok", status_code=303)
    except ValueError as e:
        return RedirectResponse(f"/bitacora/diagnostico/{codigo_diagnostico}?error={str(e)}", status_code=303)


def ctrl_bitacora_detalle(req, codigo_diagnostico: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "bitacora", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    bitacora = deps.bitacora.obtener_por_codigo(codigo_diagnostico)
    if not bitacora:
        return RedirectResponse("/bitacora", status_code=303)
    vehiculo = deps.vehiculos.obtener(bitacora.get("idVehiculo"))
    return render_bitacora_detalle(req, bitacora, vehiculo)
