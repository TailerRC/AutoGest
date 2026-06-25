"""
controllers/catalogo_ctrl.py
=============================
Controller del Catálogo Técnico (MongoDB).
"""
from auth import puede_acceder
from controllers import deps
from routes.catalogo_tecnico import render_catalogo_list


def ctrl_catalogo_list(req):
    """
    Controlador para listar el catálogo técnico con filtros avanzados y paginación.
    """
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "catalogo", "ver"):
        from routes.helpers import no_perm
        return no_perm(req)

    # 1. Obtener parámetros de búsqueda avanzada y paginación
    codigo = req.query_params.get("codigo", "").strip()
    marca  = req.query_params.get("marca", "").strip()
    modelo = req.query_params.get("modelo", "").strip()
    año_s  = req.query_params.get("año", "").strip()
    motor  = req.query_params.get("motor", "").strip()
    aceite = req.query_params.get("aceite", "").strip()

    año = int(año_s) if año_s.isdigit() else None

    try:
        page = int(req.query_params.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    # 2. Consultar catálogo filtrado por medio del servicio
    resultados = deps.catalogo.buscar(
        marca=marca, modelo=modelo, año=año,
        codigo=codigo, motor=motor, aceite=aceite
    )

    # 3. Aplicar paginación (6 registros por página)
    limit = 6
    total_count = len(resultados)
    total_pages = max(1, (total_count + limit - 1) // limit)

    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_catalogo = resultados[start_idx:end_idx]

    return render_catalogo_list(
        req, paginated_catalogo,
        codigo=codigo, marca=marca, modelo=modelo, año_s=año_s, motor=motor, aceite=aceite,
        page=page, total_pages=total_pages, total_count=total_count
    )

