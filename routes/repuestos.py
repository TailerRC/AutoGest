"""
routes/repuestos.py — View puro de Repuestos/Inventario
========================================================
Solo renderiza HTML. Lógica en controllers/repuestos_ctrl.py.
"""
from fasthtml.common import *
from auth import puede_acceder
from .helpers import layout, stock_badge


def render_repuestos_list(req, usuario, repuestos):
    """Renderiza el inventario de repuestos con alertas de stock."""
    msg = req.query_params.get("msg", "")
    alerts_map = {
        "creado":    Div("✅ Repuesto agregado al inventario.", cls="alert alert-success"),
        "editado":   Div("✅ Repuesto actualizado.", cls="alert alert-success"),
        "eliminado": Div("🗑️ Repuesto eliminado.", cls="alert alert-warning"),
    }
    alert = alerts_map.get(msg, "")

    criticos = [r for r in repuestos if r["stock"] <= 2]
    bajos    = [r for r in repuestos if 2 < r["stock"] <= 5]

    alertas_stock = []
    if criticos:
        alertas_stock.append(Div(f"⚠️ Stock CRÍTICO (≤2 unidades): {', '.join(r['nombre'] for r in criticos)}", cls="alert alert-error"))
    if bajos:
        alertas_stock.append(Div(f"⚡ Stock BAJO (≤5 unidades): {', '.join(r['nombre'] for r in bajos)}", cls="alert alert-warning"))

    stats = Div(
        Div(Div("📦", cls="stat-icon orange"), Div(Div(str(len(repuestos)), cls="stat-value"), Div("Total Ítems", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div("⚠️", cls="stat-icon red"),    Div(Div(str(len(criticos)), cls="stat-value"), Div("Stock Crítico", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div("⚡", cls="stat-icon yellow"),  Div(Div(str(len(bajos)), cls="stat-value"), Div("Stock Bajo", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        Div(Div("💰", cls="stat-icon green"),   Div(Div(f"S/. {sum(r['precio_venta']*r['stock'] for r in repuestos):,.0f}", cls="stat-value"), Div("Valor Inventario", cls="stat-label"), cls="stat-info"), cls="stat-card"),
        cls="stats-grid"
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


def render_repuestos_nuevo(req):
    """Renderiza el formulario de nuevo repuesto."""
    error = req.query_params.get("error", "")
    alert = Div(f"❌ {error}", cls="alert alert-error") if error else ""

    form = Form(
        alert,
        Div(
            Div(Label("Código"),            Input(name="codigo",      placeholder="FIL-ACE-016", required=True), cls="form-group"),
            Div(Label("Nombre"),            Input(name="nombre",      placeholder="Filtro de Aceite...", required=True), cls="form-group"),
            Div(Label("Stock inicial"),     Input(name="stock",       type="number", min="0", value="1", required=True), cls="form-group"),
            Div(Label("Precio de venta (S/.)"), Input(name="precio_venta", type="number", step="0.01", min="0", placeholder="0.00", required=True), cls="form-group"),
            Div(Label("Proveedor"),         Input(name="proveedor",   placeholder="AutoParts SAC", required=True), cls="form-group"),
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


def render_repuestos_editar(req, repuesto):
    """Renderiza el formulario de edición de un repuesto."""
    id_pieza = repuesto["id_pieza"]
    form = Form(
        Div(
            Div(Label("Código"),        Input(name="codigo",      value=repuesto["codigo"],      required=True), cls="form-group"),
            Div(Label("Nombre"),        Input(name="nombre",      value=repuesto["nombre"],      required=True), cls="form-group"),
            Div(Label("Stock"),         Input(name="stock",       type="number", min="0", value=str(repuesto["stock"]), required=True), cls="form-group"),
            Div(Label("Precio (S/.)"),  Input(name="precio_venta",type="number", step="0.01", value=str(repuesto["precio_venta"]), required=True), cls="form-group"),
            Div(Label("Proveedor"),     Input(name="proveedor",   value=repuesto["proveedor"],   required=True), cls="form-group"),
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
            Div(H2(f"✏️ Editar: {repuesto['nombre']}"), A("← Volver", href="/repuestos", cls="btn btn-secondary btn-sm"), cls="card-header"),
            Div(form, cls="card-body"),
            cls="card fade-in"
        ),
        cls="page-body"
    )
    return layout(req, "Editar Repuesto", f"✏️ {repuesto['nombre']}", "", contenido)
