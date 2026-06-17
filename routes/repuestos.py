"""
routes/repuestos.py — Inventario de Repuestos (Oracle simulado)
"""
from fasthtml.common import *
from database import get_oracle_connection
from auth import puede_acceder, registrar_accion
from .helpers import layout, no_perm, stock_badge


def repuestos_list(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "ver"):
        return no_perm(req)

    db = get_oracle_connection()
    repuestos = db.get_all_repuestos()

    msg = req.query_params.get("msg", "")
    alerts = {
        "creado":   Div("✅ Repuesto agregado al inventario.", cls="alert alert-success"),
        "editado":  Div("✅ Repuesto actualizado.", cls="alert alert-success"),
        "eliminado": Div("🗑️ Repuesto eliminado.", cls="alert alert-warning"),
    }
    alert = alerts.get(msg, "")

    # Alertas de stock bajo
    criticos = [r for r in repuestos if r["stock"] <= 2]
    bajos    = [r for r in repuestos if 2 < r["stock"] <= 5]

    alertas_stock = []
    if criticos:
        alertas_stock.append(
            Div(f"⚠️ Stock CRÍTICO (≤2 unidades): {', '.join(r['nombre'] for r in criticos)}", cls="alert alert-error")
        )
    if bajos:
        alertas_stock.append(
            Div(f"⚡ Stock BAJO (≤5 unidades): {', '.join(r['nombre'] for r in bajos)}", cls="alert alert-warning")
        )

    filas = []
    for r in repuestos:
        acciones = []
        if puede_acceder(usuario, "repuestos", "editar"):
            acciones.append(A("✏️", href=f"/repuestos/{r['id_pieza']}/editar", cls="btn btn-sm btn-blue"))
        if puede_acceder(usuario, "repuestos", "eliminar"):
            acciones.append(
                Form(
                    Input(type="hidden", name="id_pieza", value=str(r["id_pieza"])),
                    Button("🗑️", type="submit", cls="btn btn-sm btn-danger",
                           onclick="return confirm('¿Eliminar repuesto?')"),
                    method="post", action="/repuestos/eliminar"
                )
            )
        filas.append(Tr(
            Td(Span(r["codigo"], cls="font-mono text-sm text-muted")),
            Td(r["nombre"]),
            Td(stock_badge(r["stock"])),
            Td(f"S/. {r['precio_venta']:.2f}"),
            Td(r["proveedor"]),
            Td(Div(*acciones, cls="flex gap-1") if acciones else "—"),
        ))

    stats = Div(
        Div(Div("📦", cls="stat-icon orange"), Div(Div(str(len(repuestos)), cls="stat-value"), Div("Total Ítems", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div("⚠️", cls="stat-icon red"),    Div(Div(str(len(criticos)), cls="stat-value"), Div("Stock Crítico", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div("⚡", cls="stat-icon yellow"),  Div(Div(str(len(bajos)), cls="stat-value"), Div("Stock Bajo", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div("💰", cls="stat-icon green"),   Div(Div(f"S/. {sum(r['precio_venta']*r['stock'] for r in repuestos):,.0f}", cls="stat-value"), Div("Valor Inventario", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        cls="stats-grid"
    )

    crear_btn = A("＋ Nuevo Repuesto", href="/repuestos/nuevo", cls="btn btn-primary") \
        if puede_acceder(usuario, "repuestos", "crear") else ""

    tabla = Div(
        Table(
            Thead(Tr(Th("Código"), Th("Nombre"), Th("Stock"), Th("Precio Venta"), Th("Proveedor"), Th("Acciones"))),
            Tbody(*filas) if filas else Tbody(Tr(Td("Sin repuestos.", colspan="6", cls="no-data"))),
        ),
        cls="table-wrap"
    )

    contenido = Div(
        alert, *alertas_stock, stats,
        Div(
            Div(H2("🔧 Inventario de Repuestos"), cls="card-header"),
            Div(
                Div(Span(f"{len(repuestos)} ítems", cls="text-muted text-sm"), crear_btn,
                    cls="flex gap-2", style="justify-content:space-between;align-items:center;margin-bottom:1rem;"),
                tabla, cls="card-body"
            ),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Repuestos", "🔧 Inventario de Repuestos", "Base de datos Oracle", contenido)


def repuestos_nuevo(req):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "crear"):
        return no_perm(req)

    form = Form(
        Div(
            Div(Label("Código"), Input(name="codigo", placeholder="FIL-ACE-016", required=True), cls="form-group"),
            Div(Label("Nombre"), Input(name="nombre", placeholder="Filtro de Aceite...", required=True), cls="form-group"),
            Div(Label("Stock inicial"), Input(name="stock", type="number", min="0", value="1", required=True), cls="form-group"),
            Div(Label("Precio de venta (S/.)"), Input(name="precio_venta", type="number", step="0.01", min="0", placeholder="0.00", required=True), cls="form-group"),
            Div(Label("Proveedor"), Input(name="proveedor", placeholder="AutoParts SAC", required=True), cls="form-group"),
            cls="form-grid"
        ),
        Div(
            A("Cancelar", href="/repuestos", cls="btn btn-secondary"),
            Button("💾 Guardar", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/repuestos/crear"
    )

    contenido = Div(
        Div(
            Div(H2("➕ Nuevo Repuesto"), A("← Volver", href="/repuestos", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Nuevo Repuesto", "➕ Nuevo Repuesto", "", contenido)


def repuestos_crear(req, codigo: str, nombre: str, stock: int, precio_venta: float, proveedor: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "crear"):
        return no_perm(req)
    db = get_oracle_connection()
    db.create_repuesto(codigo.strip(), nombre.strip(), stock, precio_venta, proveedor.strip())
    registrar_accion(usuario, "CREAR", "repuestos")
    return RedirectResponse("/repuestos?msg=creado", status_code=303)


def repuestos_editar(req, id_pieza: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "editar"):
        return no_perm(req)

    db = get_oracle_connection()
    r = db.get_repuesto(id_pieza)
    if not r:
        return RedirectResponse("/repuestos", status_code=303)

    form = Form(
        Div(
            Div(Label("Código"), Input(name="codigo", value=r["codigo"], required=True), cls="form-group"),
            Div(Label("Nombre"), Input(name="nombre", value=r["nombre"], required=True), cls="form-group"),
            Div(Label("Stock"), Input(name="stock", type="number", min="0", value=str(r["stock"]), required=True), cls="form-group"),
            Div(Label("Precio de venta (S/.)"), Input(name="precio_venta", type="number", step="0.01", value=str(r["precio_venta"]), required=True), cls="form-group"),
            Div(Label("Proveedor"), Input(name="proveedor", value=r["proveedor"], required=True), cls="form-group"),
            cls="form-grid"
        ),
        Input(type="hidden", name="id_pieza", value=str(id_pieza)),
        Div(
            A("Cancelar", href="/repuestos", cls="btn btn-secondary"),
            Button("💾 Actualizar", type="submit", cls="btn btn-primary"),
            cls="form-actions"
        ),
        method="post", action="/repuestos/actualizar"
    )

    contenido = Div(
        Div(
            Div(H2(f"✏️ Editar: {r['nombre']}"), A("← Volver", href="/repuestos", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Editar Repuesto", f"✏️ {r['nombre']}", "", contenido)


def repuestos_actualizar(req, id_pieza: int, codigo: str, nombre: str, stock: int, precio_venta: float, proveedor: str):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "editar"):
        return no_perm(req)
    db = get_oracle_connection()
    db.update_repuesto(id_pieza, codigo.strip(), nombre.strip(), stock, precio_venta, proveedor.strip())
    registrar_accion(usuario, "EDITAR", "repuestos")
    return RedirectResponse("/repuestos?msg=editado", status_code=303)


def repuestos_eliminar(req, id_pieza: int):
    usuario = req.session.get("usuario")
    if not puede_acceder(usuario, "repuestos", "eliminar"):
        return no_perm(req)
    db = get_oracle_connection()
    db.delete_repuesto(id_pieza)
    registrar_accion(usuario, "ELIMINAR", "repuestos")
    return RedirectResponse("/repuestos?msg=eliminado", status_code=303)
