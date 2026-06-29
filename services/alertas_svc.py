"""
services/alertas_svc.py
=========================
Lógica de negocio para la generación de Alertas del Sistema (MongoDB).

Diferencia clave con log_actividad:
  - log_actividad  -> auditoría técnica de TODO lo que hace cada usuario
                       (quién hizo qué, cuándo, desde dónde).
  - alertas_sistema -> eventos de negocio que requieren atención
                       (stock bajo, retrasos, accesos denegados, pagos vencidos).

Reglas implementadas:
  1. Logística   - Stock Bajo:        stock <= RepuestoService.UMBRAL_BAJO
  2. Operaciones - Retraso:           fecha_entrega ya pasó y estado != completada
  3. Seguridad   - Acceso Denegado:   intento de login fallido
  4. Facturación - Pago Vencido:      estado_pago == pendiente y han pasado
                                       más de DIAS_VENCIMIENTO desde 'fecha'
"""
from datetime import datetime, date, timedelta
from typing import List, Dict
from repositories.mongo.logs_repo import LogsRepository
from repositories.oracle.ordenes_repo import OrdenRepository
from repositories.oracle.facturas_repo import FacturaRepository
from repositories.oracle.repuestos_repo import RepuestoRepository


class AlertaService:
    """
    Servicio de Alertas del Sistema — detecta condiciones de negocio
    y registra alertas en MongoDB (alertas_sistema), evitando duplicados.
    """

    UMBRAL_STOCK_BAJO = 5      # mismo umbral que RepuestoService.UMBRAL_BAJO
    DIAS_VENCIMIENTO_FACTURA = 15

    def __init__(self, logs_repo: LogsRepository, orden_repo: OrdenRepository,
                 factura_repo: FacturaRepository, repuesto_repo: RepuestoRepository):
        self._logs = logs_repo
        self._ord_repo = orden_repo
        self._fac_repo = factura_repo
        self._rep_repo = repuesto_repo

    # ── Lectura (para el dashboard) ───────────────────────────────────
    def listar_activas(self, limit: int = 20) -> List[Dict]:
        return self._logs.get_alertas_activas(limit=limit)

    # ── Evaluación general (se llama al cargar el dashboard) ──────────
    def evaluar_todas(self) -> None:
        """
        Revisa las 4 reglas de negocio y genera alertas nuevas si corresponde.
        Se debe llamar al cargar el dashboard. Es idempotente: si la alerta
        ya existe (misma clave), no la duplica.
        """
        self._evaluar_stock_bajo()
        self._evaluar_ordenes_retrasadas()
        self._evaluar_facturas_vencidas()

    # ── Regla 1: Logística - Stock Bajo ───────────────────────────────
    def _evaluar_stock_bajo(self) -> None:
        repuestos = self._rep_repo.get_all()
        for r in repuestos:
            if r["stock"] <= self.UMBRAL_STOCK_BAJO:
                clave = f"stock_{r['id_pieza']}"
                if self._logs.existe_alerta_similar("Logística - Stock Bajo", clave):
                    continue
                self._logs.crear_alerta(
                    tipo_evento="Logística - Stock Bajo",
                    detalle_notificacion={
                        "clave": clave,
                        "item": r["nombre"],
                        "stock_actual": r["stock"],
                        "minimo_requerido": self.UMBRAL_STOCK_BAJO,
                    }
                )

    # ── Regla 2: Operaciones - Retraso ────────────────────────────────
    def _evaluar_ordenes_retrasadas(self) -> None:
        ordenes = self._ord_repo.get_all()
        hoy = date.today()
        for o in ordenes:
            if o["estado"] == "completada" or o["estado"] == "cancelada":
                continue
            fecha_entrega = o.get("fecha_entrega")
            if not fecha_entrega:
                continue
            fecha_entrega_d = self._a_date(fecha_entrega)
            if fecha_entrega_d and fecha_entrega_d < hoy:
                clave = f"orden_{o['id_orden']}"
                if self._logs.existe_alerta_similar("Operaciones - Retraso", clave):
                    continue
                self._logs.crear_alerta(
                    tipo_evento="Operaciones - Retraso",
                    detalle_notificacion={
                        "clave": clave,
                        "idOrden": o["id_orden"],
                        "placa": o.get("placa", "—"),
                        "mensaje": f"Orden #{o['id_orden']} venció el {fecha_entrega_d.strftime('%d/%m/%Y')} y sigue {o['estado']}.",
                    }
                )

    # ── Regla 3: Seguridad - Acceso Denegado ──────────────────────────
    def registrar_login_fallido(self, username: str, motivo: str, ip: str = "desconocida") -> None:
        """
        Se llama directamente desde auth.py en cada intento fallido
        (no se evalúa en batch porque es un evento puntual, no un estado).
        """
        clave = f"login_{username}_{datetime.utcnow().strftime('%Y%m%d%H%M')}"
        self._logs.crear_alerta(
            tipo_evento="Seguridad - Acceso Denegado",
            detalle_notificacion={
                "clave": clave,
                "username": username,
                "motivo": motivo,
                "ip": ip,
            }
        )

    # ── Regla 4: Facturación - Pago Vencido ───────────────────────────
    def _evaluar_facturas_vencidas(self) -> None:
        facturas = self._fac_repo.get_all()
        hoy = date.today()
        for f in facturas:
            if f["estado_pago"] != "pendiente":
                continue
            fecha_d = self._a_date(f.get("fecha"))
            if not fecha_d:
                continue
            dias_transcurridos = (hoy - fecha_d).days
            if dias_transcurridos > self.DIAS_VENCIMIENTO_FACTURA:
                clave = f"factura_{f['id_factura']}"
                if self._logs.existe_alerta_similar("Facturación - Pago Vencido", clave):
                    continue
                self._logs.crear_alerta(
                    tipo_evento="Facturación - Pago Vencido",
                    detalle_notificacion={
                        "clave": clave,
                        "idFactura": f["id_factura"],
                        "cliente": f.get("nombre_cliente", "—"),
                        "total": f["total"],
                        "dias_vencida": dias_transcurridos - self.DIAS_VENCIMIENTO_FACTURA,
                    }
                )

    # ── Helper ─────────────────────────────────────────────────────────
    @staticmethod
    def _a_date(valor) -> date:
        """Normaliza datetime/date/str a date para poder comparar."""
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date):
            return valor
        if isinstance(valor, str):
            try:
                return datetime.strptime(valor[:10], "%Y-%m-%d").date()
            except ValueError:
                return None
        return None