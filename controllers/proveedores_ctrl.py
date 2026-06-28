"""
controllers/proveedores_ctrl.py
================================
Controlador para los Proveedores.
"""
import urllib.parse
from fasthtml.common import RedirectResponse
from controllers import deps
from auth import puede_acceder, registrar_accion
from routes.proveedores import (
    render_proveedores_list,
    render_proveedores_nuevo,
    render_proveedores_editar,
)


def ctrl_proveedores_list(req):
    """
    Controlador para listar los proveedores con soporte para búsqueda insensitiva,
    filtrado por línea de producto, ordenamiento secuencial y paginación.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "proveedores", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)

    # 1. Obtener parámetros de búsqueda, filtro y paginación
    q = req.query_params.get("q", "").strip().lower()
    linea = req.query_params.get("linea", "todos").strip()
    try:
        page = int(req.query_params.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    # 2. Consultar todos los proveedores desde MongoDB
    proveedores = deps.proveedores.listar()

    # 3. Aplicar filtros en memoria
    filtered = []
    for p in proveedores:
        contacto = p.get("contacto", {})
        lineas = p.get("lineas_productos", [])

        # Filtro de búsqueda insensitiva a mayúsculas/minúsculas
        if q:
            match_codigo = q in p.get("codigoProveedor", "").lower()
            match_razon = q in p.get("nombreEmpresa", "").lower()
            match_telefono = q in contacto.get("telefono", "").lower()
            match_email = q in contacto.get("email", "").lower()
            match_linea = any(q in l.lower() for l in lineas)

            if not (match_codigo or match_razon or match_telefono or match_email or match_linea):
                continue

        # Filtro por línea de producto
        if linea != "todos":
            if not any(linea.lower() == l.lower() for l in lineas):
                continue

        filtered.append(p)

    # 4. Ordenamiento secuencial por código de proveedor (PROV-001, PROV-002, etc.)
    def get_sort_key(prov):
        codigo = prov.get("codigoProveedor", "")
        try:
            return int(codigo.split("-")[-1])
        except Exception:
            return codigo

    filtered.sort(key=get_sort_key)

    # 5. Paginación de resultados (6 por página)
    limit = 6
    total_count = len(filtered)
    total_pages = max(1, (total_count + limit - 1) // limit)

    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_proveedores = filtered[start_idx:end_idx]

    return render_proveedores_list(
        req, usuario, paginated_proveedores,
        q=q, linea=linea,
        page=page, total_pages=total_pages, total_count=total_count
    )


def ctrl_proveedores_nuevo(req):
    """
    Controlador para renderizar la vista de nuevo proveedor.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "proveedores", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    return render_proveedores_nuevo(req)


def ctrl_proveedores_crear(req, codigo: str, nombre_empresa: str,
                           lineas_raw: str, telefono: str, email: str):
    """
    Controlador para procesar la creación de un nuevo proveedor con validaciones en Service.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "proveedores", "crear"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        lineas = [l.strip() for l in lineas_raw.split(",") if l.strip()]
        deps.proveedores.crear(codigo, nombre_empresa, lineas, telefono, email)
        registrar_accion(usuario, "CREAR", "proveedores")
        return RedirectResponse("/proveedores?msg=creado", status_code=303)
    except Exception as e:
        error_msg = urllib.parse.quote(str(e))
        return RedirectResponse(f"/proveedores/nuevo?error={error_msg}", status_code=303)


def ctrl_proveedores_editar(req, codigo: str):
    """
    Controlador para renderizar la pantalla de edición de un proveedor.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "proveedores", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    proveedor = deps.proveedores.obtener_por_codigo(codigo)
    if not proveedor:
        return RedirectResponse("/proveedores", status_code=303)
    return render_proveedores_editar(req, proveedor)


def ctrl_proveedores_actualizar(req, codigo: str, nombre_empresa: str,
                                lineas_raw: str, telefono: str, email: str):
    """
    Controlador para procesar la actualización de un proveedor existente.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "proveedores", "editar"):
        from routes.helpers import no_perm
        return no_perm(req)
    try:
        lineas = [l.strip() for l in lineas_raw.split(",") if l.strip()]
        deps.proveedores.actualizar(codigo, nombre_empresa, lineas, telefono, email)
        registrar_accion(usuario, "EDITAR", "proveedores")
        return RedirectResponse("/proveedores?msg=editado", status_code=303)
    except Exception as e:
        error_msg = urllib.parse.quote(str(e))
        return RedirectResponse(f"/proveedores/{codigo}/editar?error={error_msg}", status_code=303)
