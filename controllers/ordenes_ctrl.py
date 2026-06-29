"""
controllers/ordenes_ctrl.py
============================
Controller de Órdenes de Trabajo.
"""
from fasthtml.common import RedirectResponse, Response
from auth import puede_acceder, registrar_accion
from controllers import deps
from routes.ordenes import (
    render_ordenes_list,
    render_ordenes_detalle,
    render_ordenes_nueva,
    render_ordenes_editar,
    render_orden_pdf_html,
)


def ctrl_ordenes_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)

    try:
        page = int(req.query_params.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    todas_ordenes = deps.ordenes.listar()

    # Paginación de resultados (6 por página) — mismo patrón que Repuestos/Cotizaciones
    limit = 6
    total_count = len(todas_ordenes)
    total_pages = max(1, (total_count + limit - 1) // limit)

    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    ordenes_paginadas = todas_ordenes[start_idx:end_idx]

    return render_ordenes_list(
        req, usuario, ordenes_paginadas, todas_ordenes,
        page=page, total_pages=total_pages, total_count=total_count
    )


def ctrl_ordenes_detalle(req, id_orden: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)
    orden = deps.ordenes.obtener_detallada(id_orden)
    if not orden:
        return RedirectResponse("/ordenes", status_code=303)
    repuestos = deps.repuestos.listar()

    id_vehiculo = orden.get("vehiculo", {}).get("id_vehiculo") if orden.get("vehiculo") else None
    vigentes = deps.cotizaciones.listar_vigentes_por_vehiculo(id_vehiculo) if id_vehiculo else []
    cotizacion_vehiculo = vigentes[0] if vigentes else None

    return render_ordenes_detalle(req, usuario, orden, repuestos, cotizacion_vehiculo)


def ctrl_ordenes_nueva(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    vehiculos = deps.vehiculos.listar()
    mecanicos = deps.empleados.listar_mecanicos()

    # Cotizaciones vigentes por vehículo, para el modal "Ver Cotizaciones"
    cotizaciones_por_vehiculo = {}
    for v in vehiculos:
        vigentes = deps.cotizaciones.listar_vigentes_por_vehiculo(v["id_vehiculo"])
        if vigentes:
            cotizaciones_por_vehiculo[v["id_vehiculo"]] = vigentes

    return render_ordenes_nueva(req, vehiculos, mecanicos, cotizaciones_por_vehiculo)


def ctrl_ordenes_crear(req, id_vehiculo: int, id_empleado: int,
                        fecha_ingreso: str, fecha_entrega: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    nueva = deps.ordenes.crear(id_vehiculo, id_empleado, fecha_ingreso, fecha_entrega)
    registrar_accion(usuario, "CREAR", "ordenes")
    return RedirectResponse(f"/ordenes/{nueva['id_orden']}?msg=creado", status_code=303)


def ctrl_ordenes_editar(req, id_orden: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    orden = deps.ordenes.obtener(id_orden)
    if not orden:
        return RedirectResponse("/ordenes", status_code=303)
    vehiculos = deps.vehiculos.listar()
    empleados = deps.empleados.listar()
    return render_ordenes_editar(req, orden, vehiculos, empleados)


def ctrl_ordenes_actualizar(req, id_orden: int, id_vehiculo: int,
                             id_empleado: int, fecha_ingreso: str,
                             fecha_entrega: str, estado: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    deps.ordenes.actualizar(id_orden, id_vehiculo, id_empleado,
                             fecha_ingreso, fecha_entrega, estado)
    registrar_accion(usuario, "EDITAR", "ordenes")
    return RedirectResponse(f"/ordenes/{id_orden}?msg=actualizado", status_code=303)


def ctrl_ordenes_cambiar_estado(req, id_orden: int, estado: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    deps.ordenes.cambiar_estado(id_orden, estado)
    registrar_accion(usuario, "CAMBIAR_ESTADO", "ordenes")
    return RedirectResponse(f"/ordenes/{id_orden}?msg=actualizado", status_code=303)


def ctrl_ordenes_agregar_repuesto(req, id_orden: int, id_pieza: int,
                                   cantidad: int, precio_unitario: float):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.ordenes.agregar_repuesto(id_orden, id_pieza, cantidad, precio_unitario)
        registrar_accion(usuario, "AGREGAR_REPUESTO", "ordenes")
        return RedirectResponse(f"/ordenes/{id_orden}?msg=detalle_agregado", status_code=303)
    except ValueError as e:
        return RedirectResponse(f"/ordenes/{id_orden}?error={str(e)}", status_code=303)


def ctrl_ordenes_cargar_cotizacion(req, id_orden: int, codigo_cotizacion: str):
    """
    Carga una cotización vigente en una orden existente:
    clasifica cada línea contra el inventario, inserta los repuestos
    reales en DETALLE_ORDEN_REPUESTOS, y deja los servicios como informativos.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)

    cotizacion = deps.cotizaciones.obtener_por_codigo(codigo_cotizacion)
    if not cotizacion:
        return RedirectResponse(f"/ordenes/{id_orden}?error=Cotización no encontrada", status_code=303)

    repuestos_inventario = deps.repuestos.listar()

    try:
        resumen = deps.ordenes.cargar_cotizacion(id_orden, cotizacion, repuestos_inventario)
        registrar_accion(usuario, "CARGAR_COTIZACION", "ordenes")

        import urllib.parse
        msg = f"cotizacion_cargada&repuestos={len(resumen['repuestos_cargados'])}&servicios={len(resumen['servicios'])}"
        if resumen["advertencias"]:
            advertencia_txt = urllib.parse.quote(" | ".join(resumen["advertencias"]))
            return RedirectResponse(
                f"/ordenes/{id_orden}?msg=cotizacion_cargada&advertencia={advertencia_txt}",
                status_code=303
            )
        return RedirectResponse(f"/ordenes/{id_orden}?msg=cotizacion_cargada", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/ordenes/{id_orden}?error={str(e)}", status_code=303)


def ctrl_ordenes_imprimir(req, id_orden: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)

    orden = deps.ordenes.obtener_detallada(id_orden)
    if not orden:
        return RedirectResponse("/ordenes", status_code=303)
    if orden.get("estado") != "completada":
        return RedirectResponse(f"/ordenes/{id_orden}?error=Solo se puede imprimir una orden completada", status_code=303)

    repuestos = deps.repuestos.listar()
    id_vehiculo = orden.get("vehiculo", {}).get("id_vehiculo") if orden.get("vehiculo") else None
    vigentes = deps.cotizaciones.listar_vigentes_por_vehiculo(id_vehiculo) if id_vehiculo else []

    servicios_cotizacion = []
    if vigentes:
        clasificacion = deps.ordenes.clasificar_cotizacion(vigentes[0], repuestos)
        servicios_cotizacion = clasificacion["servicios"]

    from xhtml2pdf import pisa
    from io import BytesIO

    html_content = render_orden_pdf_html(orden, servicios_cotizacion)
    buffer = BytesIO()
    pisa.CreatePDF(html_content, dest=buffer)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=orden_{id_orden}.pdf"}
    )

def ctrl_ordenes_quitar_repuesto(req, id_orden: int, id_detalle: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "ordenes", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    deps.ordenes.quitar_repuesto(id_detalle)
    registrar_accion(usuario, "QUITAR_REPUESTO", "ordenes")
    return RedirectResponse(f"/ordenes/{id_orden}?msg=repuesto_quitado", status_code=303)