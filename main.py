"""
main.py — AutoGest: Sistema de Gestión de Taller Mecánico y Concesionaria
Universidad Ricardo Palma — Base de Datos II

Arquitectura híbrida:
  - Oracle simulado (8 tablas relacionales) → mock_data/oracle_data.py
  - MongoDB simulado (7 colecciones) → mock_data/mongo_data.py

Para ejecutar:
  python main.py   (o:  uvicorn main:app --reload)

Usuarios de prueba:
  admin       / admin123   → acceso total
  mecanico1   / mec2026    → mecánico
  facturacion / fact2026   → facturación
  readonly    / view2026   → solo lectura
"""

from fasthtml.common import *
from auth import login, puede_acceder, registrar_accion
from database import get_oracle_connection, get_mongo_connection
import os
from dotenv import load_dotenv
from starlette.datastructures import UploadFile

FOTOS_PATH = os.getenv("FOTOS_VEHICULOS_PATH", "fotos_vehiculos")

# ── Importar helpers ──────────────────────────────────────────────────
from routes.helpers import layout, login_layout, no_perm, badge_estado

# ── Importar módulos de controllers ───────────────────────────────────
from controllers.clientes_ctrl import (
    ctrl_clientes_list, ctrl_clientes_nuevo, ctrl_clientes_crear,
    ctrl_clientes_editar, ctrl_clientes_actualizar, ctrl_clientes_eliminar,
)
from controllers.vehiculos_ctrl import (
    ctrl_vehiculos_list, ctrl_vehiculos_nuevo, ctrl_vehiculos_crear,
    ctrl_vehiculos_editar, ctrl_vehiculos_actualizar, ctrl_vehiculos_eliminar,
)
from controllers.empleados_ctrl import (
    ctrl_empleados_list, ctrl_empleados_nuevo, ctrl_empleados_crear,
    ctrl_empleados_editar, ctrl_empleados_actualizar, ctrl_empleados_eliminar,
)
from controllers.ordenes_ctrl import (
    ctrl_ordenes_list, ctrl_ordenes_detalle, ctrl_ordenes_nueva, ctrl_ordenes_crear,
    ctrl_ordenes_editar, ctrl_ordenes_actualizar, ctrl_ordenes_cambiar_estado,
    ctrl_ordenes_agregar_repuesto,
)
from controllers.repuestos_ctrl import (
    ctrl_repuestos_list, ctrl_repuestos_nuevo, ctrl_repuestos_crear,
    ctrl_repuestos_editar, ctrl_repuestos_actualizar, ctrl_repuestos_eliminar,
)
from controllers.facturas_ctrl import (
    ctrl_facturas_list, ctrl_facturas_detalle, ctrl_facturas_nueva,
    ctrl_facturas_crear, ctrl_facturas_cambiar_estado,
)
from controllers.usuarios_ctrl import (
    ctrl_usuarios_list, ctrl_usuarios_nuevo, ctrl_usuarios_crear,
    ctrl_usuarios_editar, ctrl_usuarios_actualizar, ctrl_usuarios_desactivar,
)
from controllers.catalogo_ctrl import ctrl_catalogo_list
from controllers.bitacora_ctrl import (
    ctrl_bitacora_list, ctrl_bitacora_nueva, ctrl_bitacora_crear, ctrl_bitacora_detalle
)
from controllers.reportes_ctrl import ctrl_reportes_list, ctrl_reportes_detalle

from controllers.historial_ctrl import ctrl_historial_list, ctrl_historial_nuevo, ctrl_historial_crear
from controllers.cotizaciones_ctrl import (
    ctrl_cotizaciones_list, ctrl_cotizaciones_nueva, ctrl_cotizaciones_crear, ctrl_cotizaciones_detalle
)
from controllers.proveedores_ctrl import (
    ctrl_proveedores_list, ctrl_proveedores_nuevo, ctrl_proveedores_crear,
    ctrl_proveedores_editar, ctrl_proveedores_actualizar
)
from controllers import deps

load_dotenv()

# ═══════════════════════════════════════════════════════════════════════
# Inicialización de la aplicación FastHTML
# ═══════════════════════════════════════════════════════════════════════
app, rt = fast_app(
    secret_key=os.getenv("SECRET_KEY", "dev_secret_key"),
    static_path="static",
    hdrs=(
        Link(rel="stylesheet", href="/fontawesome/css/all.min.css"),
        Link(rel="stylesheet", href="/styles/styles.css"),
    ),
    live=False,
)


# ═══════════════════════════════════════════════════════════════════════
# Middleware — verificar sesión en cada petición protegida
# ═══════════════════════════════════════════════════════════════════════
def require_login(req) -> bool:
    """Retorna True si el usuario está logueado, False si no."""
    return bool(req.session.get("usuario"))


# ═══════════════════════════════════════════════════════════════════════
# RUTAS DE AUTENTICACIÓN
# ═══════════════════════════════════════════════════════════════════════

@rt("/")
def get(req):
    """Redirige al login o al dashboard según sesión."""
    if require_login(req):
        return RedirectResponse("/dashboard", status_code=303)
    return RedirectResponse("/login", status_code=303)


@rt("/login")
def get(req):
    """Pantalla de login."""
    if require_login(req):
        return RedirectResponse("/dashboard", status_code=303)

    error = req.query_params.get("error", "")
    alert = Div(f"❌ {error}", cls="alert alert-error") if error else ""

    form = Form(
        Div(
            Div(
                Img(src="/image/Logo.png", alt="AutoGest"),
                cls="logo-img-wrap"
            ),
            H1("AutoGest"),
            P("Sistema de Gestión de Taller Mecánico (Autogest)"),
            cls="login-logo"
        ),
        alert,
        Div(
            Div(
                Label("Usuario", style="font-size:.78rem;font-weight:600;color:var(--text-secondary);text-transform:uppercase;letter-spacing:.05em;"),
                Input(name="username", placeholder="Ingresa tu usuario", required=True,
                      autocomplete="username", id="username"),
                style="display:flex;flex-direction:column;gap:.4rem;margin-bottom:1rem;"
            ),
            Div(
                Label("Contraseña", style="font-size:.78rem;font-weight:600;color:var(--text-secondary);text-transform:uppercase;letter-spacing:.05em;"),
                Input(name="password", type="password", placeholder="••••••••",
                      required=True, autocomplete="current-password", id="password"),
                style="display:flex;flex-direction:column;gap:.4rem;margin-bottom:1.25rem;"
            ),
        ),
        Button(I(cls="fa-solid fa-right-to-bracket"), " Iniciar Sesión", type="submit", cls="btn btn-primary btn-full btn-lg"),
        Div(
            P("Usuarios de demo:"),
            Div(
                Span("ana.gomez / admin123", cls="badge badge-purple"),
                Span("pedro.ramirez / mec2026", cls="badge badge-blue"),
                Span("luis.torres / fact2026", cls="badge badge-orange"),
                Span("diego.vargas / view2026", cls="badge badge-gray"),
                style="display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.5rem;"
            ),
            style="margin-top:1.25rem;padding-top:1rem;border-top:1px solid var(--border);font-size:.75rem;color:var(--text-muted);"
        ),
        method="post", action="/login",
        style="display:flex;flex-direction:column;"
    )

    return login_layout("Iniciar Sesión", Div(form, cls="login-card"))


@rt("/login")
def post(req, username: str, password: str):
    """Procesa el login."""
    ip = req.client.host if req.client else "desconocida"
    usuario = login(username, password, ip)
    if not usuario:
        return RedirectResponse("/login?error=Usuario+o+contraseña+incorrectos", status_code=303)
    req.session["usuario"] = usuario
    return RedirectResponse("/dashboard", status_code=303)


@rt("/logout")
def get(req):
    """Cierra sesión."""
    usuario = req.session.get("usuario")
    if usuario:
        registrar_accion(usuario, "LOGOUT", "auth")
    req.session.clear()
    return RedirectResponse("/login", status_code=303)


# ═══════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════

@rt("/dashboard")
def get(req):
    if not require_login(req):
        return RedirectResponse("/login", status_code=303)

    usuario = req.session.get("usuario")

    clientes   = deps.clientes.listar()
    vehiculos  = deps.vehiculos.listar()
    ordenes    = deps.ordenes.listar()
    repuestos  = deps.repuestos.listar()
    facturas   = deps.facturas.listar()

    # Evalúa las reglas de negocio y genera alertas nuevas si corresponde
    # (stock bajo, retraso de órdenes, facturas vencidas). Es idempotente.
    deps.alertas.evaluar_todas()
    alertas = deps.alertas.listar_activas(limit=8)

    stats_estados = deps.ordenes.get_stats_estados(ordenes)
    pendientes  = stats_estados["pendiente"]
    en_proceso  = stats_estados["en_proceso"]
    completadas = stats_estados["completada"]
    canceladas  = stats_estados["cancelada"]

    criticos    = len(deps.repuestos.listar_criticos())
    pendiente_cobro = sum(f["total"] for f in facturas if f["estado_pago"] == "pendiente")
    pagado_total     = sum(f["total"] for f in facturas if f["estado_pago"] == "pagada")
    
    # Órdenes por mecánico (para el gráfico de barras)
    conteo_mecanico = {}
    for o in ordenes:
        nombre = o.get("nombre_empleado", "Sin asignar")
        conteo_mecanico[nombre] = conteo_mecanico.get(nombre, 0) + 1
    mecanicos_labels = list(conteo_mecanico.keys())
    mecanicos_data   = list(conteo_mecanico.values())

    # Stock crítico por repuesto (para el gráfico de barras horizontal)
    repuestos_criticos_chart = deps.repuestos.listar_criticos()[:8]
    stock_labels = [r["nombre"] for r in repuestos_criticos_chart]
    stock_data   = [r["stock"] for r in repuestos_criticos_chart]

    def stat_card(icon, valor, label, color, trend=None):
        trend_el = Span(trend, cls="stat-trend") if trend else ""
        return Div(
            Div(I(cls=icon), cls=f"stat-icon {color}"),
            Div(
                Div(valor, cls="stat-value"),
                Div(label, cls="stat-label"),
                trend_el,
                cls="stat-info"
            ),
            cls="stat-card"
        )

    stats = Div(
        stat_card("fa-solid fa-users", str(len(clientes)), "Clientes", "cyan"),
        stat_card("fa-solid fa-car", str(len(vehiculos)), "Vehículos", "blue"),
        stat_card("fa-solid fa-clipboard-list", str(len(ordenes)), "Órdenes", "indigo"),
        stat_card("fa-solid fa-triangle-exclamation", str(criticos), "Stock Crítico", "red"),
        stat_card("fa-solid fa-sack-dollar", f"S/. {pendiente_cobro:,.0f}", "Por Cobrar", "green"),
        cls="stats-grid"
    )

    # Alertas del sistema (MongoDB) — renderizado legible, no el dict crudo
    ICONOS_ALERTA = {
        "Logística - Stock Bajo":         ("fa-solid fa-box-open",          "badge-yellow"),
        "Operaciones - Retraso":          ("fa-solid fa-clock",             "badge-orange"),
        "Seguridad - Acceso Denegado":    ("fa-solid fa-user-lock",         "badge-red"),
        "Facturación - Pago Vencido":     ("fa-solid fa-file-circle-exclamation", "badge-red"),
    }

    def _texto_alerta(a: dict) -> str:
        """Convierte detalle_notificacion en una frase legible, según el tipo de evento."""
        tipo = a.get("tipo_evento", "")
        d = a.get("detalle_notificacion", {})
        if tipo == "Logística - Stock Bajo":
            return f"{d.get('item','—')}: quedan {d.get('stock_actual','—')} unidades (mínimo {d.get('minimo_requerido','—')})"
        if tipo == "Operaciones - Retraso":
            return d.get("mensaje", f"Orden #{d.get('idOrden','—')} con retraso")
        if tipo == "Seguridad - Acceso Denegado":
            return f"Usuario '{d.get('username','—')}' — {d.get('motivo','—')} (IP: {d.get('ip','—')})"
        if tipo == "Facturación - Pago Vencido":
            return f"Factura #{d.get('idFactura','—')} de {d.get('cliente','—')} — S/. {d.get('total',0):,.2f}, vencida hace {d.get('dias_vencida','—')} días"
        return str(d)

    alertas_cards = []
    for a in alertas:
        tipo = a.get("tipo_evento", "")
        icono, badge_cls = ICONOS_ALERTA.get(tipo, ("fa-solid fa-bell", "badge-gray"))
        alertas_cards.append(
            Div(
                Div(
                    Span(I(cls=icono), " ", tipo, cls=f"badge {badge_cls}"),
                    Span(a.get("codigoAlerta", ""), cls="text-muted text-sm font-mono"),
                    style="display:flex;align-items:center;justify-content:space-between;"
                ),
                P(_texto_alerta(a), style="margin-top:.4rem;font-size:.85rem;color:var(--text-secondary);"),
                style="padding:.75rem;background:rgba(255,255,255,.03);border:1px solid var(--border);border-radius:var(--radius);margin-bottom:.5rem;"
            )
        )

    # Últimas órdenes — ya vienen ordenadas DESC por id_orden desde el repo
    # (VW_ORDENES_TRABAJO ORDER BY id_orden DESC), así que tomamos las primeras 5
    # SIN invertir. El bug anterior aplicaba reversed() sobre un slice del final
    # de una lista que ya estaba en orden ascendente — daba las más antiguas.
    ultimas = ordenes[:5]
    filas_ord = [
        Tr(
            Td(f"#{o['id_orden']}", cls="font-mono text-sm"),
            Td(o.get("nombre_cliente","—")),
            Td(Span(o.get("placa",""), cls="badge badge-gray font-mono")),
            Td(badge_estado(o["estado"])),
            Td(A("Ver", href=f"/ordenes/{o['id_orden']}", cls="btn btn-sm btn-secondary")),
        )
        for o in ultimas
    ]

    nombre_u = usuario.get("username","")
    rol_u    = usuario.get("rol","")

    contenido = Div(
        # Bienvenida
        Div(
            H2(I(cls="fa-solid fa-hand-wave"), f" ¡Bienvenido, {nombre_u}!"),
            P("Sesión activa como: ", Span(rol_u.capitalize(), cls="badge badge-blue"), cls="text-muted text-sm mt-1"),
            cls="dashboard-welcome"
        ),
        stats,
        # Gráficos del dashboard (Chart.js)
        Div(
            Div(
                Div(H2(I(cls="fa-solid fa-chart-pie"), " Órdenes por Estado"), cls="card-header"),
                Div(
                    Div(
                        Canvas(id="chartEstados", role="img",
                               aria_label=f"Gráfico circular de órdenes por estado: {pendientes} pendientes, {en_proceso} en proceso, {completadas} completadas, {canceladas} canceladas"),
                        style="position:relative;height:190px;"
                    ),
                    Div(id="legendEstados", cls="chart-legend"),
                    cls="card-body"
                ),
                cls="card"
            ),
            Div(
                Div(H2(I(cls="fa-solid fa-sack-dollar"), " Facturas: Pagadas vs Pendientes"), cls="card-header"),
                Div(
                    Div(
                        Canvas(id="chartFacturas", role="img",
                               aria_label=f"Gráfico circular de facturas: S/. {pagado_total:,.0f} pagado, S/. {pendiente_cobro:,.0f} pendiente de cobro"),
                        style="position:relative;height:190px;"
                    ),
                    Div(id="legendFacturas", cls="chart-legend"),
                    cls="card-body"
                ),
                cls="card"
            ),
            cls="dashboard-charts-grid"
        ),
        Div(
            Div(
                Div(H2(I(cls="fa-solid fa-boxes-stacked"), " Stock Crítico por Repuesto"), cls="card-header"),
                Div(
                    Div(
                        Canvas(id="chartStock", role="img",
                               aria_label="Gráfico circular de repuestos con stock crítico, mostrando nombre y cantidad disponible de cada uno"),
                        style="position:relative;height:190px;"
                    ) if stock_labels else P("Sin repuestos en estado crítico.", cls="no-data"),
                    Div(id="legendStock", cls="chart-legend") if stock_labels else "",
                    cls="card-body"
                ),
                cls="card"
            ),
            Div(
                Div(H2(I(cls="fa-solid fa-user-gear"), " Órdenes por Mecánico"), cls="card-header"),
                Div(
                    Div(
                        Canvas(id="chartMecanicos", role="img",
                               aria_label="Gráfico circular de cantidad de órdenes atendidas por cada mecánico"),
                        style="position:relative;height:190px;"
                    ),
                    Div(id="legendMecanicos", cls="chart-legend"),
                    cls="card-body"
                ),
                cls="card"
            ),
            cls="dashboard-charts-grid"
        ),
    # Dos columnas
        Div(
            Div(
                Div(
                    Div(H2(I(cls="fa-solid fa-clipboard-list"), " Últimas Órdenes"), cls="card-header"),
                    Div(
                        Div(
                            Table(
                                Thead(Tr(Th("#"), Th("Cliente"), Th("Placa"), Th("Estado"), Th(""))),
                                Tbody(*filas_ord),
                            ),
                            cls="table-wrap"
                        ),
                        cls="card-body"
                    ),
                    cls="card"
                ),
                style="flex:1.5;"
            ),
            Div(
                Div(
                    Div(H2(I(cls="fa-solid fa-bell"), " Alertas del Sistema"), cls="card-header"),
                    Div(
                        Div(
                            *alertas_cards if alertas_cards else [P("Sin alertas activas.", cls="no-data")],
                            cls="scroll-panel"
                        ),
                        cls="card-body"
                    ),
                    cls="card"
                ),
                style="flex:1;"
            ),
            cls="flex gap-2", style="align-items:stretch;"
        ),
    )

    chart_script = Script(f"""
    (function() {{
        const colorBorgona = '#7A0C11';
        const colorIndigo  = '#4A2E80';
        const colorAzul    = '#3B82F6';
        const colorCian    = '#06B6D4';
        const colorVerde   = '#10B981';
        const colorAmbar   = '#F59E0B';
        const colorRojo    = '#EF4444';
        const colorTeal    = '#0d9488';
        const paletaDonut  = [colorBorgona, colorIndigo, colorAzul, colorCian, colorVerde, colorAmbar, colorRojo, colorTeal];

        function crearLeyenda(contenedorId, labels, data, sufijo) {{
            const cont = document.getElementById(contenedorId);
            if (!cont) return;
            cont.innerHTML = '';
            labels.forEach(function(label, i) {{
                const item = document.createElement('div');
                item.className = 'chart-legend-item';
                const dot = document.createElement('span');
                dot.className = 'dot';
                dot.style.background = paletaDonut[i % paletaDonut.length];
                const lbl = document.createElement('span');
                lbl.className = 'legend-label';
                lbl.textContent = label;
                lbl.title = label;
                const val = document.createElement('span');
                val.className = 'legend-value';
                val.textContent = data[i] + (sufijo || '');
                item.appendChild(dot);
                item.appendChild(lbl);
                item.appendChild(val);
                cont.appendChild(item);
            }});
        }}

        // 1. Órdenes por estado (dona)
        const estadosLabels = ['Pendiente', 'En Proceso', 'Completada', 'Cancelada'];
        const estadosData = [{pendientes}, {en_proceso}, {completadas}, {canceladas}];
        new Chart(document.getElementById('chartEstados'), {{
            type: 'doughnut',
            data: {{
                labels: estadosLabels,
                datasets: [{{
                    data: estadosData,
                    backgroundColor: [colorAmbar, colorAzul, colorVerde, colorRojo],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});
        crearLeyenda('legendEstados', estadosLabels, estadosData);

        // 2. Facturas pagadas vs pendientes (dona)
        const facturasLabels = ['Pagado', 'Pendiente de cobro'];
        const facturasData = [{pagado_total}, {pendiente_cobro}];
        new Chart(document.getElementById('chartFacturas'), {{
            type: 'doughnut',
            data: {{
                labels: facturasLabels,
                datasets: [{{
                    data: facturasData,
                    backgroundColor: [colorVerde, colorBorgona],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(ctx) {{
                                return ctx.label + ': S/. ' + ctx.parsed.toLocaleString('es-PE', {{minimumFractionDigits: 2}});
                            }}
                        }}
                    }}
                }}
            }}
        }});
        crearLeyenda('legendFacturas', facturasLabels, facturasData.map(v => 'S/. ' + v.toLocaleString('es-PE', {{minimumFractionDigits: 0}})), '');

        // 3. Stock crítico por repuesto (circular)
        const stockLabels = {stock_labels!r};
        const stockData = {stock_data!r};
        if (stockLabels.length > 0) {{
            new Chart(document.getElementById('chartStock'), {{
                type: 'doughnut',
                data: {{
                    labels: stockLabels,
                    datasets: [{{
                        data: stockData,
                        backgroundColor: paletaDonut.slice(0, stockLabels.length),
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            callbacks: {{
                                label: function(ctx) {{
                                    return ctx.label + ': ' + ctx.parsed + ' unidades';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            crearLeyenda('legendStock', stockLabels, stockData, ' u.');
        }}

        // 4. Órdenes por mecánico (circular)
        const mecanicosLabels = {mecanicos_labels!r};
        const mecanicosData = {mecanicos_data!r};
        new Chart(document.getElementById('chartMecanicos'), {{
            type: 'doughnut',
            data: {{
                labels: mecanicosLabels,
                datasets: [{{
                    data: mecanicosData,
                    backgroundColor: paletaDonut.slice(0, mecanicosLabels.length),
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(ctx) {{
                                return ctx.label + ': ' + ctx.parsed + ' órdenes';
                            }}
                        }}
                    }}
                }}
            }}
        }});
        crearLeyenda('legendMecanicos', mecanicosLabels, mecanicosData, ' ord.');
    }})();
    """)

    return layout(req, "Dashboard", "Dashboard", f"AutoGest — {len(ordenes)} órdenes activas",
                   Div(contenido, Script(src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"), chart_script))


# ═══════════════════════════════════════════════════════════════════════
# CLIENTES
# ═══════════════════════════════════════════════════════════════════════
@rt("/clientes")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_clientes_list(req)

@rt("/clientes/nuevo")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_clientes_nuevo(req)

@rt("/clientes/crear")
def post(req, nombre: str, dni: str, telefono: str, email: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_clientes_crear(req, nombre, dni, telefono, email)

@rt("/clientes/{id_cliente}/editar")
def get(req, id_cliente: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_clientes_editar(req, id_cliente)

@rt("/clientes/actualizar")
def post(req, id_cliente: int, nombre: str, dni: str, telefono: str, email: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_clientes_actualizar(req, id_cliente, nombre, dni, telefono, email)

@rt("/clientes/eliminar")
def post(req, id_cliente: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_clientes_eliminar(req, id_cliente)


# ═══════════════════════════════════════════════════════════════════════
# VEHÍCULOS
# ═══════════════════════════════════════════════════════════════════════
@rt("/vehiculos")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_vehiculos_list(req)

@rt("/vehiculos/nuevo")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_vehiculos_nuevo(req)

@rt("/vehiculos/crear")
def post(req, id_cliente: int, placa: str, marca: str, modelo: str, anio: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_vehiculos_crear(req, id_cliente, placa, marca, modelo, anio)

@rt("/vehiculos/{id_vehiculo}/editar")
def get(req, id_vehiculo: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_vehiculos_editar(req, id_vehiculo)

@rt("/vehiculos/actualizar")
def post(req, id_vehiculo: int, id_cliente: int, placa: str, marca: str, modelo: str, anio: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_vehiculos_actualizar(req, id_vehiculo, id_cliente, placa, marca, modelo, anio)

@rt("/vehiculos/eliminar")
def post(req, id_vehiculo: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_vehiculos_eliminar(req, id_vehiculo)

@rt("/vehiculos/{id_vehiculo}/fotos")
async def post(req, id_vehiculo: int):
    if not require_login(req):
        return RedirectResponse("/login", status_code=303)

    form     = await req.form()
    placa    = form.get("placa", "").upper().strip()
    frontal  = form.get("foto_frontal")
    lateral  = form.get("foto_lateral")
    angular  = form.get("foto_angular")

    archivos = {
        "FRONTAL": frontal,
        "LATERAL": lateral,
        "ANGULAR": angular,
    }

    # Validar que las 3 estén presentes
    for vista, archivo in archivos.items():
        if not archivo or not getattr(archivo, "filename", None):
            return RedirectResponse(
                f"/vehiculos/{id_vehiculo}/editar?error=Debes+subir+las+3+fotos+({vista}+falta)",
                status_code=303
            )

    # Crear carpeta {PLACA}_FOTOS dentro de la ruta general
    carpeta = os.path.join(FOTOS_PATH, f"{placa}_FOTOS")
    os.makedirs(carpeta, exist_ok=True)

    # Guardar cada foto
    for vista, archivo in archivos.items():
        ext     = os.path.splitext(archivo.filename)[1].lower() or ".jpg"
        nombre  = f"{placa}_{vista}{ext}"
        destino = os.path.join(carpeta, nombre)
        contenido = await archivo.read()
        with open(destino, "wb") as f:
            f.write(contenido)

    return RedirectResponse(
        f"/vehiculos/{id_vehiculo}/editar?msg=fotos_ok",
        status_code=303
    )

# ═══════════════════════════════════════════════════════════════════════
# EMPLEADOS
# ═══════════════════════════════════════════════════════════════════════
@rt("/empleados")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_empleados_list(req)

@rt("/empleados/nuevo")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_empleados_nuevo(req)

@rt("/empleados/crear")
def post(req, nombre: str, cargo: str, especialidad: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_empleados_crear(req, nombre, cargo, especialidad)

@rt("/empleados/{id_empleado}/editar")
def get(req, id_empleado: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_empleados_editar(req, id_empleado)

@rt("/empleados/actualizar")
def post(req, id_empleado: int, nombre: str, cargo: str, especialidad: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_empleados_actualizar(req, id_empleado, nombre, cargo, especialidad)

@rt("/empleados/eliminar")
def post(req, id_empleado: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_empleados_eliminar(req, id_empleado)

# ═══════════════════════════════════════════════════════════════════════
# ÓRDENES DE TRABAJO
# ═══════════════════════════════════════════════════════════════════════
@rt("/ordenes")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_ordenes_list(req)

@rt("/ordenes/nueva")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_ordenes_nueva(req)

@rt("/ordenes/crear")
def post(req, id_vehiculo: int, id_empleado: int, fecha_ingreso: str, fecha_entrega: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_ordenes_crear(req, id_vehiculo, id_empleado, fecha_ingreso, fecha_entrega)

@rt("/ordenes/{id_orden}")
def get(req, id_orden: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_ordenes_detalle(req, id_orden)

@rt("/ordenes/{id_orden}/editar")
def get(req, id_orden: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_ordenes_editar(req, id_orden)

@rt("/ordenes/actualizar")
def post(req, id_orden: int, id_vehiculo: int, id_empleado: int,
         fecha_ingreso: str, fecha_entrega: str, estado: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_ordenes_actualizar(req, id_orden, id_vehiculo, id_empleado, fecha_ingreso, fecha_entrega, estado)

@rt("/ordenes/cambiar-estado")
def post(req, id_orden: int, estado: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_ordenes_cambiar_estado(req, id_orden, estado)

@rt("/ordenes/agregar-repuesto")
def post(req, id_orden: int, id_pieza: int, cantidad: int, precio_unitario: float):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_ordenes_agregar_repuesto(req, id_orden, id_pieza, cantidad, precio_unitario)


# ═══════════════════════════════════════════════════════════════════════
# REPUESTOS / INVENTARIO
# ═══════════════════════════════════════════════════════════════════════
@rt("/repuestos")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_repuestos_list(req)

@rt("/repuestos/nuevo")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_repuestos_nuevo(req)

@rt("/repuestos/crear")
def post(req, codigo: str, nombre: str, stock: int, precio_venta: float, proveedor: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_repuestos_crear(req, codigo, nombre, stock, precio_venta, proveedor)

@rt("/repuestos/{id_pieza}/editar")
def get(req, id_pieza: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_repuestos_editar(req, id_pieza)

@rt("/repuestos/actualizar")
def post(req, id_pieza: int, codigo: str, nombre: str, stock: int, precio_venta: float, proveedor: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_repuestos_actualizar(req, id_pieza, codigo, nombre, stock, precio_venta, proveedor)

@rt("/repuestos/eliminar")
def post(req, id_pieza: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_repuestos_eliminar(req, id_pieza)


# ═══════════════════════════════════════════════════════════════════════
# FACTURAS
# ═══════════════════════════════════════════════════════════════════════
@rt("/facturas")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_facturas_list(req)

@rt("/facturas/nueva")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_facturas_nueva(req)

@rt("/facturas/crear")
def post(req, id_orden: int, total: float, metodo_pago: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_facturas_crear(req, id_orden, total, metodo_pago)

@rt("/facturas/{id_factura}")
def get(req, id_factura: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_facturas_detalle(req, id_factura)

@rt("/facturas/cambiar-estado")
def post(req, id_factura: int, estado_pago: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_facturas_cambiar_estado(req, id_factura, estado_pago)


# ═══════════════════════════════════════════════════════════════════════
# USUARIOS (solo admin)
# ═══════════════════════════════════════════════════════════════════════
@rt("/usuarios")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_usuarios_list(req)

@rt("/usuarios/nuevo")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_usuarios_nuevo(req)

@rt("/usuarios/crear")
def post(req, id_empleado: int, username: str, password: str, rol: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_usuarios_crear(req, id_empleado, username, password, rol)

@rt("/usuarios/{id_usuario}/editar")
def get(req, id_usuario: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_usuarios_editar(req, id_usuario)

@rt("/usuarios/actualizar")
def post(req, id_usuario: int, id_empleado: int, username: str,
         password: str = None, rol: str = None, estado: str = None):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_usuarios_actualizar(req, id_usuario, id_empleado, username, password, rol, estado)

@rt("/usuarios/desactivar")
def post(req, id_usuario: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_usuarios_desactivar(req, id_usuario)


# ═══════════════════════════════════════════════════════════════════════
# CATÁLOGO TÉCNICO (MongoDB)
# ═══════════════════════════════════════════════════════════════════════
@rt("/catalogo")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_catalogo_list(req)


# ═══════════════════════════════════════════════════════════════════════
# BITÁCORA DE DIAGNÓSTICO (MongoDB)
# ═══════════════════════════════════════════════════════════════════════
@rt("/bitacora")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_bitacora_list(req)

@rt("/bitacora/nueva")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_bitacora_nueva(req)

@rt("/bitacora/crear")
def post(req, id_vehiculo: int, id_empleado: int, codigo_especificacion: str,
         sintomas: str, codigos_obd: str = "", observaciones: str = ""):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_bitacora_crear(req, id_vehiculo, id_empleado, codigo_especificacion,
                               sintomas, codigos_obd, observaciones)

@rt("/bitacora/{id_orden}")
def get(req, id_orden: int):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_bitacora_detalle(req, id_orden)


# ═══════════════════════════════════════════════════════════════════════
# REPORTES COMBINADOS (Oracle + MongoDB)
# ═══════════════════════════════════════════════════════════════════════
@rt("/reportes")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_reportes_list(req)

@rt("/reportes/detalle")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_reportes_detalle(req)

# ═══════════════════════════════════════════════════════════════════════
# HISTORIAL, COTIZACIONES, PROVEEDORES (MongoDB)
# ═══════════════════════════════════════════════════════════════════════

# Historial
@rt("/historial")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_historial_list(req)

@rt("/historial/nuevo")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_historial_nuevo(req)

@rt("/historial/crear")
def post(req, id_vehiculo: int, kilometraje_ingreso: int, fecha_servicio: str, estado_final: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_historial_crear(req, id_vehiculo, kilometraje_ingreso, fecha_servicio, estado_final)


# ── MÓDULO COTIZACIONES (MongoDB) ──────────────────────────────────────
# Gestión NoSQL de proformas pre-servicio. Integra colecciones de MongoDB
# con llaves foráneas a tablas relacionales de Oracle (Clientes/Vehículos).

@rt("/cotizaciones")
def get(req):
    """
    Ruta GET /cotizaciones
    Lista las cotizaciones registradas. Soporta parámetros de consulta q, estado, orden y page
    para búsqueda, filtrado, ordenamiento y paginación a nivel de controlador.
    """
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_cotizaciones_list(req)

@rt("/cotizaciones/nueva")
def get(req):
    """
    Ruta GET /cotizaciones/nueva
    Muestra el formulario dinámico multilínea para redactar una proforma.
    """
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_cotizaciones_nueva(req)

@rt("/cotizaciones/crear")
def post(req, id_cliente: int, id_vehiculo: int, fecha_validez: str, items_json: str, total: float):
    """
    Ruta POST /cotizaciones/crear
    Recibe la información en formato JSON desde el frontend para validar y guardar
    el documento de cotización con ítems embebidos en MongoDB.
    """
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_cotizaciones_crear(req, id_cliente, id_vehiculo, fecha_validez, items_json, total)

@rt("/cotizaciones/{codigo}")
def get(req, codigo: str):
    """
    Ruta GET /cotizaciones/{codigo}
    Muestra el detalle estructurado de una proforma consultando el documento en MongoDB.
    """
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_cotizaciones_detalle(req, codigo)

# Proveedores
@rt("/proveedores")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_proveedores_list(req)

@rt("/proveedores/nuevo")
def get(req):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_proveedores_nuevo(req)

@rt("/proveedores/crear")
def post(req, codigo: str, nombre_empresa: str, lineas_raw: str, telefono: str, email: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_proveedores_crear(req, codigo, nombre_empresa, lineas_raw, telefono, email)

@rt("/proveedores/{codigo}/editar")
def get(req, codigo: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_proveedores_editar(req, codigo)

@rt("/proveedores/actualizar")
def post(req, codigo: str, nombre_empresa: str, lineas_raw: str, telefono: str, email: str):
    if not require_login(req): return RedirectResponse("/login", status_code=303)
    return ctrl_proveedores_actualizar(req, codigo, nombre_empresa, lineas_raw, telefono, email)


# ═══════════════════════════════════════════════════════════════════════
# Punto de entrada
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    import sys
    # Fix Windows console encoding
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("\n" + "="*60)
    print("  [*]  AutoGest - Sistema de Gestion de Taller Mecanico")
    print("  [U]  Universidad Ricardo Palma - Base de Datos II")
    print("="*60)
    print("\n  [>]  Abre: http://localhost:5001")
    print("\n  [i]  Usuarios de prueba:")
    print("       admin       / admin123   -> Acceso total")
    print("       mecanico1   / mec2026    -> Mecanico")
    print("       facturacion / fact2026   -> Facturacion")
    print("       readonly    / view2026   -> Solo lectura")
    print("\n" + "="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=5001, reload=False)
