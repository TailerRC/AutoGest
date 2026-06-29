"""
controllers/repuestos_ctrl.py
==============================
Controller de Repuestos / Inventario.
"""
from fasthtml.common import RedirectResponse
from auth import puede_acceder, registrar_accion
from controllers import deps
from routes.repuestos import (
    render_repuestos_list,
    render_repuestos_nuevo,
    render_repuestos_editar,
)


def ctrl_repuestos_list(req):
    """
    Controlador para listar el inventario de repuestos con filtros, ordenación y paginación.
    INTEGRACIÓN: Los repuestos son consultados por Cotizaciones y Citas de Trabajo.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)

    # 0. Verificar si es una consulta de detalle de alerta para modal dinámico
    detalle_alerta = req.query_params.get("detalle_alerta", "").strip().lower()
    if detalle_alerta:
        repuestos = deps.repuestos.listar()
        if detalle_alerta == "critico":
            items = [r for r in repuestos if r["stock"] <= 2]
        elif detalle_alerta == "bajo":
            items = [r for r in repuestos if 2 < r["stock"] <= 5]
        else:
            items = []
        from routes.repuestos import render_detalle_alerta_fragment
        return render_detalle_alerta_fragment(items)

    # 1. Obtener parámetros del request
    q = req.query_params.get("q", "").strip().lower()
    filtro_stock = req.query_params.get("filtro_stock", "todos").strip().lower()
    orden = req.query_params.get("orden", "nombre_asc").strip()
    try:
        page = int(req.query_params.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    # 2. Obtener lista completa de repuestos desde Oracle
    repuestos = deps.repuestos.listar()

    # 3. Filtrar en memoria
    filtered = []
    for r in repuestos:
        # Búsqueda por código, nombre y proveedor
        if q:
            match_codigo = q in r.get("codigo", "").lower()
            match_nombre = q in r.get("nombre", "").lower()
            match_proveedor = q in r.get("proveedor", "").lower()
            if not (match_codigo or match_nombre or match_proveedor):
                continue

        # Filtro de Stock
        stock = r.get("stock", 0)
        if filtro_stock == "critico":
            if stock > 2:
                continue
        elif filtro_stock == "bajo":
            if stock > 5:
                continue
        elif filtro_stock == "normal":
            if stock <= 5:
                continue

        filtered.append(r)

    # 4. Ordenar en memoria
    if orden == "nombre_asc":
        filtered.sort(key=lambda x: x.get("nombre", "").lower())
    elif orden == "nombre_desc":
        filtered.sort(key=lambda x: x.get("nombre", "").lower(), reverse=True)
    elif orden == "stock_desc":
        filtered.sort(key=lambda x: x.get("stock", 0), reverse=True)
    elif orden == "stock_asc":
        filtered.sort(key=lambda x: x.get("stock", 0))
    elif orden == "precio_desc":
        filtered.sort(key=lambda x: x.get("precio_venta", 0.0), reverse=True)
    elif orden == "precio_asc":
        filtered.sort(key=lambda x: x.get("precio_venta", 0.0))

    # 5. Paginación de resultados (6 por página)
    limit = 6
    total_count = len(filtered)
    total_pages = max(1, (total_count + limit - 1) // limit)

    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_repuestos = filtered[start_idx:end_idx]

    # Pasamos también la lista completa para estadísticas e integraciones
    return render_repuestos_list(
        req, usuario, paginated_repuestos, repuestos,
        q=q, filtro_stock=filtro_stock, orden=orden,
        page=page, total_pages=total_pages, total_count=total_count
    )


def ctrl_repuestos_nuevo(req):
    """
    Controlador para mostrar el formulario de nuevo repuesto.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    return render_repuestos_nuevo(req)


def ctrl_repuestos_crear(req, codigo: str, nombre: str, stock: int,
                          precio_venta: float, proveedor: str):
    """
    Controlador para procesar la creación de un nuevo repuesto.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.repuestos.crear(codigo, nombre, stock, precio_venta, proveedor)
        registrar_accion(usuario, "CREAR", "repuestos")
        return RedirectResponse("/repuestos?msg=creado", status_code=303)
    except ValueError as e:
        import urllib.parse
        error_msg = urllib.parse.quote(str(e))
        return RedirectResponse(f"/repuestos/nuevo?error={error_msg}", status_code=303)


def ctrl_repuestos_editar(req, id_pieza: int):
    """
    Controlador para renderizar el formulario de edición de repuesto.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    repuesto = deps.repuestos.obtener(id_pieza)
    if not repuesto:
        return RedirectResponse("/repuestos", status_code=303)
    return render_repuestos_editar(req, repuesto)


def ctrl_repuestos_actualizar(req, id_pieza: int, codigo: str, nombre: str,
                               stock: int, precio_venta: float, proveedor: str):
    """
    Controlador para procesar la actualización de un repuesto existente.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    deps.repuestos.actualizar(id_pieza, codigo, nombre, stock, precio_venta, proveedor)
    registrar_accion(usuario, "EDITAR", "repuestos")
    return RedirectResponse("/repuestos?msg=editado", status_code=303)


def ctrl_repuestos_eliminar(req, id_pieza: int):
    """
    Controlador para procesar la eliminación segura de un repuesto.
    INTEGRACIÓN: Si tiene dependencias de foreign key en Oracle, el servicio/repo lanzará error.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "eliminar"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        deps.repuestos.eliminar(id_pieza)
        registrar_accion(usuario, "ELIMINAR", "repuestos")
        return RedirectResponse("/repuestos?msg=eliminado", status_code=303)
    except ValueError as e:
        import urllib.parse
        error_msg = urllib.parse.quote(str(e))
        return RedirectResponse(f"/repuestos?error={error_msg}", status_code=303)

