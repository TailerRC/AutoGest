"""
mock_data/mongo_data.py
========================
Simula las 7 colecciones de MongoDB como listas de diccionarios Python.
Se ha removido el uso explícito de _id simulando el comportamiento de MongoDB
donde el _id es manejado internamente (ObjectId).

Colecciones:
1. catalogo_especificaciones_tecnicas
2. bitacora_diagnostico
3. historial_mantenimiento_vehiculo
4. cotizaciones
5. proveedores
6. log_actividad
7. alertas_sistema
"""

from datetime import datetime

# ─────────────────────────────────────────────
# 1. catalogo_especificaciones_tecnicas (5 registros)
# ─────────────────────────────────────────────
CATALOGO_ESPECIFICACIONES = [
    { "codigoEspecificacion": "ESP-TOY-001", "marca": "Toyota", "modelo": "Yaris", "anio": 2018, "detalles_tecnicos": { "motor": "1.5L", "aceite": "5W-30", "bujias": "Iridium" } },
    { "codigoEspecificacion": "ESP-NCO-001", "marca": "Nissan", "modelo": "Sentra", "anio": 2017, "detalles_tecnicos": { "motor": "1.8L", "aceite": "5W-30", "transmision": "CVT" } },
    { "codigoEspecificacion": "ESP-HND-001", "marca": "Honda", "modelo": "Civic", "anio": 2016, "detalles_tecnicos": { "motor": "1.5T", "aceite": "0W-20", "presion_turbo": "16psi" } },
    { "codigoEspecificacion": "ESP-HYU-001", "marca": "Hyundai", "modelo": "Elantra", "anio": 2015, "detalles_tecnicos": { "motor": "1.6L", "aceite": "5W-30", "frenos": "Disco x4" } },
    { "codigoEspecificacion": "ESP-KIA-001", "marca": "Kia", "modelo": "Rio", "anio": 2019, "detalles_tecnicos": { "motor": "1.4L", "aceite": "5W-30", "batería": "12V 45Ah" } }
]


# ─────────────────────────────────────────────
# 2. bitacora_diagnostico (5 registros)
# ─────────────────────────────────────────────
BITACORA_DIAGNOSTICO = [
    { "codigoDiagnostico": "DIAG-001", "idVehiculo": 101, "idEmpleado": 1, "codigoEspecificacion": "ESP-TOY-001", "sintomas": ["Falta de potencia"], "codigo_OBD": ["P0301"], "fotografias_url": ["http://nube.com"], "observaciones": "Bujía del cilindro 1 desgastada" },
    { "codigoDiagnostico": "DIAG-002", "idVehiculo": 104, "idEmpleado": 1, "codigoEspecificacion": "ESP-NCO-001", "sintomas": ["Tirones en marcha"], "codigo_OBD": ["P0720"], "fotografias_url": ["http://nube.com"], "observaciones": "Falla en sensor de velocidad de salida CVT" },
    { "codigoDiagnostico": "DIAG-003", "idVehiculo": 107, "idEmpleado": 1, "codigoEspecificacion": "ESP-HND-001", "sintomas": ["Luz Check Engine"], "codigo_OBD": ["P0234"], "fotografias_url": [], "observaciones": "Condición de sobrepresión en el turbocompresor" },
    { "codigoDiagnostico": "DIAG-004", "idVehiculo": 109, "idEmpleado": 2, "codigoEspecificacion": "ESP-HYU-001", "sintomas": ["Pedal de freno largo"], "codigo_OBD": [], "fotografias_url": [], "observaciones": "Presencia de aire en las líneas de freno" },
    { "codigoDiagnostico": "DIAG-005", "idVehiculo": 111, "idEmpleado": 1, "codigoEspecificacion": "ESP-KIA-001", "sintomas": ["Vibración excesiva"], "codigo_OBD": [], "fotografias_url": [], "observaciones": "Soportes de motor rotos del lado derecho" }
]


# ─────────────────────────────────────────────
# 3. historial_mantenimiento_vehiculo (5 registros)
# ─────────────────────────────────────────────
HISTORIAL_MANTENIMIENTO = [
    { "idVehiculo": 101, "kilometraje_ingreso": 45000, "fecha_servicio": "2026-01-10", "diagnosticos_asociados": ["DIAG-001"], "estado_final": "Reparado" },
    { "idVehiculo": 104, "kilometraje_ingreso": 88000, "fecha_servicio": "2026-01-18", "diagnosticos_asociados": ["DIAG-002"], "estado_final": "Reparado" },
    { "idVehiculo": 107, "kilometraje_ingreso": 54000, "fecha_servicio": "2026-01-25", "diagnosticos_asociados": ["DIAG-003"], "estado_final": "Observado" },
    { "idVehiculo": 109, "kilometraje_ingreso": 125000, "fecha_servicio": "2026-02-01", "diagnosticos_asociados": ["DIAG-004"], "estado_final": "Reparado" },
    { "idVehiculo": 111, "kilometraje_ingreso": 67000, "fecha_servicio": "2026-02-05", "diagnosticos_asociados": ["DIAG-005"], "estado_final": "Reparado" }
]


# ─────────────────────────────────────────────
# 4. cotizaciones (5 registros)
# ─────────────────────────────────────────────
COTIZACIONES = [
    { "codigoCotizacion": "COT-2026-001", "idCliente": 1, "idVehiculo": 1, "fecha_validez": "2026-07-15T00:00:00Z", "servicios_repuestos": [{"item": "Cambio Aceite", "precio": 120.0}, {"item": "Filtro Aceite", "precio": 45.0}], "total": 165.0 },
    { "codigoCotizacion": "COT-2026-002", "idCliente": 2, "idVehiculo": 2, "fecha_validez": "2026-07-15T00:00:00Z", "servicios_repuestos": [{"item": "Pastillas Freno", "precio": 180.0}], "total": 180.0 },
    { "codigoCotizacion": "COT-2026-003", "idCliente": 3, "idVehiculo": 3, "fecha_validez": "2026-07-16T00:00:00Z", "servicios_repuestos": [{"item": "Alineamiento", "precio": 80.0}, {"item": "Balanceo", "precio": 60.0}], "total": 140.0 },
    { "codigoCotizacion": "COT-2026-004", "idCliente": 4, "idVehiculo": 4, "fecha_validez": "2026-07-16T00:00:00Z", "servicios_repuestos": [{"item": "Mano de Obra Motor", "precio": 450.0}, {"item": "Empaque Culata", "precio": 150.0}], "total": 600.0 },
    { "codigoCotizacion": "COT-2026-005", "idCliente": 5, "idVehiculo": 5, "fecha_validez": "2026-07-17T00:00:00Z", "servicios_repuestos": [{"item": "Limpieza Inyectores", "precio": 140.0}], "total": 140.0 }
]


# ─────────────────────────────────────────────
# 5. proveedores (5 registros)
# ─────────────────────────────────────────────
PROVEEDORES = [
    { "codigoProveedor": "PROV-001", "nombreEmpresa": "Importaciones Repuestos SAC", "lineas_productos": ["Frenos", "Filtros"], "contacto": { "telefono": "999888771", "email": "contacto@importrepuestos.pe" } },
    { "codigoProveedor": "PROV-002", "nombreEmpresa": "Frenos y Embragues Lima", "lineas_productos": ["Frenos", "Embragues"], "contacto": { "telefono": "999888772", "email": "ventas@frenoslima.pe" } },
    { "codigoProveedor": "PROV-003", "nombreEmpresa": "Filtros Industriales del Perú", "lineas_productos": ["Filtros"], "contacto": { "telefono": "999888773", "email": "info@filtrosperu.com" } },
    { "codigoProveedor": "PROV-004", "nombreEmpresa": "Baterías y Energía Automotriz", "lineas_productos": ["Baterias", "Electricidad"], "contacto": { "telefono": "999888774", "email": "soporte@bateriasenergia.pe" } },
    { "codigoProveedor": "PROV-005", "nombreEmpresa": "Lubricantes del Pacífico", "lineas_productos": ["Lubricantes", "Aditivos"], "contacto": { "telefono": "999888775", "email": "ventas@lubricantespacifico.com" } }
]


# ─────────────────────────────────────────────
# 6. log_actividad (5 registros)
# ─────────────────────────────────────────────
LOG_ACTIVIDAD = [
    { "idUsuario": 1, "accion": "Crear Diagnóstico", "entidad_afectada": "bitacora_diagnostico", "id_registro_afectado": "DIAG-2026-001", "detalles": { "motivo": "Ingreso regular por falla eléctrica" }, "direccion_ip": "192.168.1.50", "fecha_hora": "2026-06-22T08:00:00Z" },
    { "idUsuario": 2, "accion": "Crear Cotización", "entidad_afectada": "cotizaciones", "id_registro_afectado": "COT-2026-001", "detalles": { "monto": 165.0 }, "direccion_ip": "192.168.1.51", "fecha_hora": "2026-06-22T08:15:00Z" },
    { "idUsuario": 1, "accion": "Actualizar Historial", "entidad_afectada": "historial_mantenimiento_vehiculo", "id_registro_afectado": "HIST-001", "detalles": { "campo": "estado_final", "anterior": "En Proceso", "nuevo": "Reparado" }, "direccion_ip": "192.168.1.50", "fecha_hora": "2026-06-22T09:00:00Z" },
    { "idUsuario": 3, "accion": "Crear Alerta", "entidad_afectada": "alertas_sistema", "id_registro_afectado": "ALER-001", "detalles": { "nivel": "Critico", "mensaje": "Falta Stock" }, "direccion_ip": "192.168.1.100", "fecha_hora": "2026-06-22T09:30:00Z" },
    { "idUsuario": 4, "accion": "Crear Proveedor", "entidad_afectada": "proveedores", "id_registro_afectado": "PROV-001", "detalles": { "razon_social": "Importaciones Repuestos SAC" }, "direccion_ip": "192.168.1.60", "fecha_hora": "2026-06-22T11:00:00Z" }
]


# ─────────────────────────────────────────────
# 7. alertas_sistema (5 registros)
# ─────────────────────────────────────────────
ALERTAS_SISTEMA = [
    { "codigoAlerta": "ALER-001", "tipo_evento": "Logística - Stock Bajo", "detalle_notificacion": { "item": "Pastillas de Freno Toyota", "stock_actual": 2, "minimo_requerido": 10 } },
    { "codigoAlerta": "ALER-002", "tipo_evento": "Logística - Stock Bajo", "detalle_notificacion": { "item": "Filtro de Aceite Hyundai", "stock_actual": 1, "minimo_requerido": 15 } },
    { "codigoAlerta": "ALER-003", "tipo_evento": "Operaciones - Retraso", "detalle_notificacion": { "idOrden": 105, "mensaje": "Vehículo en espera de repuesto por más de 48 horas" } },
    { "codigoAlerta": "ALER-004", "tipo_evento": "Seguridad - Acceso Denegado", "detalle_notificacion": { "username": "mecanico_test", "ip": "192.168.1.115", "intentos": 3 } },
    { "codigoAlerta": "ALER-005", "tipo_evento": "Logística - Stock Crítico", "detalle_notificacion": { "item": "Batería 13 Placas Bosch", "stock_actual": 0, "minimo_requerido": 5 } }
]

def next_mongo_id(collection) -> str:
    # Como el Mongo genera ObjectIds, este mock genera ids de string por ahora
    # en caso de ser necesario
    import uuid
    return str(uuid.uuid4())
