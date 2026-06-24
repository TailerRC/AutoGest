"""
routes/helpers.py — Componentes UI reutilizables para FastHTML
"""
from fasthtml.common import *
from auth import get_menu, PERMISOS


# ─────────────────────────────────────────────────────────────────────
# Layout principal con sidebar + topbar
# ─────────────────────────────────────────────────────────────────────

def layout(req, title: str, page_title: str, page_subtitle: str, contenido):
    """Genera el layout completo con sidebar y topbar."""
    usuario = req.session.get("usuario", {})
    menu_items = get_menu(usuario)
    current_path = req.url.path

    rol = usuario.get("rol", "")
    nombre_usuario = usuario.get("username", "?")
    initial = nombre_usuario[0].upper() if nombre_usuario else "?"

    # Construir ítems del menú
    nav_links = []
    for item in menu_items:
        is_active = current_path.startswith(item["href"]) and (
            item["href"] == "/dashboard" and current_path == "/dashboard"
            or item["href"] != "/dashboard"
        )
        cls = "nav-item active" if is_active else "nav-item"
        nav_links.append(
            A(
                I(cls=item["icon"] + " nav-icon"),
                Span(item["label"]),
                href=item["href"], cls=cls
            )
        )

    sidebar = Aside(
        # Brand — Logo
        Div(
            Div(
                Img(
                    src="/image/Logo.png",
                    alt="AutoGest Logo",
                    cls="sidebar-logo-img"
                ),
                Div(
                    H2("AutoGest"),
                    Span("Taller & Concesionaria"),
                    cls="brand-text"
                ),
                cls="sidebar-brand-inner"
            ),
            cls="sidebar-brand"
        ),
        # User info
        Div(
            Div(
                Div(initial, cls="user-avatar"),
                Div(
                    Div(nombre_usuario, cls="user-name"),
                    Div(rol, cls="user-role"),
                    cls="user-details"
                ),
                cls="user-info"
            ),
            cls="sidebar-user"
        ),
        # Nav sections
        Nav(
            Div("PRINCIPAL", cls="nav-label"),
            *nav_links,
            cls="sidebar-nav"
        ),
        # Footer
        Div(
            A(
                I(cls="fa-solid fa-right-from-bracket"),
                " Cerrar Sesión",
                href="/logout", cls="btn btn-logout btn-sm btn-full"
            ),
            cls="sidebar-footer"
        ),
        cls="sidebar"
    )

    topbar = Header(
        Div(
            H1(page_title),
            P(page_subtitle) if page_subtitle else "",
            cls="topbar-title"
        ),
        Div(
            Span(
                I(cls="fa-solid fa-database"), " Oracle",
                cls="db-pill oracle"
            ),
            Span(
                I(cls="fa-solid fa-leaf"), " MongoDB",
                cls="db-pill mongo"
            ),
            cls="topbar-actions"
        ),
        cls="topbar"
    )

    return Html(
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Title(f"{title} — AutoGest"),
            Link(rel="stylesheet", href="/fontawesome/css/all.min.css"),
            Link(rel="stylesheet", href="/styles/styles.css"),
        ),
        Body(
            Div(
                sidebar,
                Div(topbar, contenido, cls="main-content"),
                cls="app-layout"
            )
        )
    )


def login_layout(title: str, contenido):
    """Layout minimal para la pantalla de login."""
    return Html(
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Title(f"{title} — AutoGest"),
            Link(rel="stylesheet", href="/fontawesome/css/all.min.css"),
            Link(rel="stylesheet", href="/styles/styles.css"),
        ),
        Body(Div(contenido, cls="login-page"))
    )


# ─────────────────────────────────────────────────────────────────────
# Componentes reutilizables
# ─────────────────────────────────────────────────────────────────────

def no_perm(req):
    """Página de acceso denegado."""
    usuario = req.session.get("usuario", {})
    contenido = Div(
        Div(
            Div(
                I(cls="fa-solid fa-lock"), " Acceso Denegado",
                cls="card-header"
            ),
            Div(
                Div(
                    I(cls="fa-solid fa-ban"), " Sin permisos para esta acción.",
                    cls="alert alert-error"
                ),
                P("Tu rol no tiene acceso a este módulo o acción. Contacta al administrador.", cls="text-muted"),
                A(
                    I(cls="fa-solid fa-arrow-left"), " Volver al Dashboard",
                    href="/dashboard", cls="btn btn-secondary mt-2"
                ),
                cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Sin Permiso", "Acceso Denegado", "", contenido)


def badge_estado(estado: str):
    """Genera un badge coloreado según el estado de una orden/factura."""
    mapa = {
        "pendiente":   ("badge-yellow",  I(cls="fa-solid fa-clock"),       " Pendiente"),
        "en_proceso":  ("badge-blue",    I(cls="fa-solid fa-gears"),        " En Proceso"),
        "completada":  ("badge-green",   I(cls="fa-solid fa-circle-check"), " Completada"),
        "cancelada":   ("badge-red",     I(cls="fa-solid fa-circle-xmark"), " Cancelada"),
        "pagada":      ("badge-green",   I(cls="fa-solid fa-circle-check"), " Pagada"),
        "activo":      ("badge-green",   I(cls="fa-solid fa-circle-check"), " Activo"),
        "inactivo":    ("badge-red",     I(cls="fa-solid fa-circle-xmark"), " Inactivo"),
        "aprobada":    ("badge-green",   I(cls="fa-solid fa-circle-check"), " Aprobada"),
        "activa":      ("badge-orange",  I(cls="fa-solid fa-bell"),         " Activa"),
    }
    if estado in mapa:
        css, icon, label = mapa[estado]
        return Span(icon, label, cls=f"badge {css}")
    return Span(estado, cls="badge badge-gray")


def badge_rol(rol: str):
    mapa = {
        "admin":       ("badge-purple", I(cls="fa-solid fa-crown"),       " Admin"),
        "mecanico":    ("badge-blue",   I(cls="fa-solid fa-wrench"),      " Mecánico"),
        "facturacion": ("badge-orange", I(cls="fa-solid fa-file-invoice")," Facturación"),
        "readonly":    ("badge-gray",   I(cls="fa-solid fa-eye"),         " Solo Lectura"),
    }
    if rol in mapa:
        css, icon, label = mapa[rol]
        return Span(icon, label, cls=f"badge {css}")
    return Span(rol, cls="badge badge-gray")


def badge_pago(metodo: str):
    mapa = {
        "Efectivo":        "badge-green",
        "Tarjeta Débito":  "badge-blue",
        "Tarjeta Crédito": "badge-indigo",
        "Transferencia":   "badge-cyan",
    }
    css = mapa.get(metodo, "badge-gray")
    return Span(metodo, cls=f"badge {css}")


def stock_badge(stock: int):
    if stock <= 2:
        return Span(I(cls="fa-solid fa-triangle-exclamation"), f" {stock}", cls="stock-critical")
    elif stock <= 5:
        return Span(I(cls="fa-solid fa-bolt"), f" {stock}", cls="stock-low")
    return Span(I(cls="fa-solid fa-check"), f" {stock}", cls="stock-ok")
