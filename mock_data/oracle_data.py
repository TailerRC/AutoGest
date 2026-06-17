"""
mock_data/oracle_data.py
========================
Simula las 8 tablas relacionales de Oracle como estructuras Python.
Cada lista de diccionarios representa una tabla con sus columnas.

TODO: Para migrar a Oracle real, reemplazar estas estructuras por
      consultas SQL usando cx_Oracle:
      import cx_Oracle
      conn = cx_Oracle.connect(user, password, dsn)
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM CLIENTES")
"""

from datetime import date, datetime

# ─────────────────────────────────────────────
# 1. CLIENTES
# ─────────────────────────────────────────────
CLIENTES = [
    {"id_cliente": 1, "nombre": "Carlos Mendoza Rivera",    "telefono": "987-654-321", "dni": "72345678", "email": "carlos.mendoza@gmail.com"},
    {"id_cliente": 2, "nombre": "Lucía Torres Paredes",     "telefono": "956-123-456", "dni": "45678901", "email": "lucia.torres@hotmail.com"},
    {"id_cliente": 3, "nombre": "Roberto Quispe Mamani",    "telefono": "912-345-678", "dni": "63219874", "email": "rquispe@yahoo.com"},
    {"id_cliente": 4, "nombre": "Ana Flores Ccama",         "telefono": "934-567-890", "dni": "71234567", "email": "ana.flores@gmail.com"},
    {"id_cliente": 5, "nombre": "Miguel Chávez López",      "telefono": "976-543-210", "dni": "58901234", "email": "mchavez@outlook.com"},
    {"id_cliente": 6, "nombre": "Patricia Huanca Ticona",   "telefono": "945-678-901", "dni": "80123456", "email": "p.huanca@gmail.com"},
    {"id_cliente": 7, "nombre": "Jorge Salas Benítez",      "telefono": "921-234-567", "dni": "67890123", "email": "jsalas@empresa.pe"},
    {"id_cliente": 8, "nombre": "Rosa Vargas Castillo",     "telefono": "965-432-109", "dni": "54321098", "email": "rvargas@gmail.com"},
    {"id_cliente": 9, "nombre": "Eduardo Pinto Reyes",      "telefono": "978-901-234", "dni": "43210987", "email": "epinto@hotmail.com"},
    {"id_cliente": 10,"nombre": "Sofía Gutiérrez Mora",     "telefono": "932-109-876", "dni": "32109876", "email": "sofia.gutierrez@gmail.com"},
]

# ─────────────────────────────────────────────
# 2. VEHICULOS
# ─────────────────────────────────────────────
VEHICULOS = [
    {"id_vehiculo": 1,  "id_cliente": 1,  "placa": "ABC-123", "marca": "Toyota",   "modelo": "Corolla",   "año": 2019},
    {"id_vehiculo": 2,  "id_cliente": 2,  "placa": "DEF-456", "marca": "Hyundai",  "modelo": "Accent",    "año": 2020},
    {"id_vehiculo": 3,  "id_cliente": 3,  "placa": "GHI-789", "marca": "Kia",      "modelo": "Rio",       "año": 2018},
    {"id_vehiculo": 4,  "id_cliente": 4,  "placa": "JKL-012", "marca": "Nissan",   "modelo": "Sentra",    "año": 2021},
    {"id_vehiculo": 5,  "id_cliente": 5,  "placa": "MNO-345", "marca": "Chevrolet","modelo": "Aveo",      "año": 2017},
    {"id_vehiculo": 6,  "id_cliente": 6,  "placa": "PQR-678", "marca": "Toyota",   "modelo": "Yaris",     "año": 2022},
    {"id_vehiculo": 7,  "id_cliente": 7,  "placa": "STU-901", "marca": "Honda",    "modelo": "Civic",     "año": 2020},
    {"id_vehiculo": 8,  "id_cliente": 8,  "placa": "VWX-234", "marca": "Mazda",    "modelo": "3",         "año": 2019},
    {"id_vehiculo": 9,  "id_cliente": 9,  "placa": "YZA-567", "marca": "Kia",      "modelo": "Sportage",  "año": 2023},
    {"id_vehiculo": 10, "id_cliente": 10, "placa": "BCD-890", "marca": "Hyundai",  "modelo": "Tucson",    "año": 2021},
]

# ─────────────────────────────────────────────
# 3. EMPLEADOS
# ─────────────────────────────────────────────
EMPLEADOS = [
    {"id_empleado": 1, "nombre": "Luis Alberto Romero",   "cargo": "Jefe de Taller",        "especialidad": "Mecánica General"},
    {"id_empleado": 2, "nombre": "Marco Ticona Huayta",   "cargo": "Mecánico Senior",        "especialidad": "Motor y Transmisión"},
    {"id_empleado": 3, "nombre": "Kevin Soto Bernales",   "cargo": "Mecánico",               "especialidad": "Electricidad Automotriz"},
    {"id_empleado": 4, "nombre": "Diana Castro Quiroz",   "cargo": "Asistente Administrativo","especialidad": "Gestión y Facturación"},
    {"id_empleado": 5, "nombre": "Raúl Ponce Delgado",    "cargo": "Mecánico",               "especialidad": "Frenos y Suspensión"},
]

# ─────────────────────────────────────────────
# 4. ORDENES_TRABAJO
# ─────────────────────────────────────────────
ORDENES_TRABAJO = [
    {"id_orden": 1,  "id_vehiculo": 1,  "id_empleado": 2, "fecha_ingreso": "2026-05-10", "fecha_entrega": "2026-05-12", "estado": "completada"},
    {"id_orden": 2,  "id_vehiculo": 3,  "id_empleado": 3, "fecha_ingreso": "2026-05-15", "fecha_entrega": "2026-05-17", "estado": "completada"},
    {"id_orden": 3,  "id_vehiculo": 5,  "id_empleado": 5, "fecha_ingreso": "2026-05-20", "fecha_entrega": "2026-05-22", "estado": "en_proceso"},
    {"id_orden": 4,  "id_vehiculo": 2,  "id_empleado": 2, "fecha_ingreso": "2026-05-25", "fecha_entrega": "2026-05-27", "estado": "completada"},
    {"id_orden": 5,  "id_vehiculo": 7,  "id_empleado": 3, "fecha_ingreso": "2026-06-01", "fecha_entrega": "2026-06-03", "estado": "en_proceso"},
    {"id_orden": 6,  "id_vehiculo": 4,  "id_empleado": 5, "fecha_ingreso": "2026-06-05", "fecha_entrega": "2026-06-07", "estado": "pendiente"},
    {"id_orden": 7,  "id_vehiculo": 6,  "id_empleado": 2, "fecha_ingreso": "2026-06-08", "fecha_entrega": "2026-06-10", "estado": "pendiente"},
    {"id_orden": 8,  "id_vehiculo": 9,  "id_empleado": 3, "fecha_ingreso": "2026-06-10", "fecha_entrega": "2026-06-12", "estado": "en_proceso"},
    {"id_orden": 9,  "id_vehiculo": 8,  "id_empleado": 5, "fecha_ingreso": "2026-06-12", "fecha_entrega": "2026-06-14", "estado": "pendiente"},
    {"id_orden": 10, "id_vehiculo": 10, "id_empleado": 2, "fecha_ingreso": "2026-06-15", "fecha_entrega": "2026-06-17", "estado": "en_proceso"},
]

# ─────────────────────────────────────────────
# 5. INVENTARIO_REPUESTOS
# ─────────────────────────────────────────────
INVENTARIO_REPUESTOS = [
    {"id_pieza": 1,  "codigo": "FIL-ACE-001", "nombre": "Filtro de Aceite Toyota",       "stock": 25, "precio_venta": 35.00,  "proveedor": "AutoParts SAC"},
    {"id_pieza": 2,  "codigo": "FIL-AIR-002", "nombre": "Filtro de Aire Universal",      "stock": 18, "precio_venta": 45.00,  "proveedor": "AutoParts SAC"},
    {"id_pieza": 3,  "codigo": "PAS-FRE-003", "nombre": "Pastillas de Freno Delanteras", "stock": 3,  "precio_venta": 120.00, "proveedor": "FrenoPeru EIRL"},
    {"id_pieza": 4,  "codigo": "BUJ-NGK-004", "nombre": "Bujías NGK (x4)",               "stock": 30, "precio_venta": 80.00,  "proveedor": "ElectroParts Peru"},
    {"id_pieza": 5,  "codigo": "COR-ALT-005", "nombre": "Correa de Alternador",          "stock": 2,  "precio_venta": 65.00,  "proveedor": "AutoParts SAC"},
    {"id_pieza": 6,  "codigo": "ACE-5W30-006","nombre": "Aceite Motor 5W-30 (4L)",       "stock": 40, "precio_venta": 95.00,  "proveedor": "Lubricantes del Sur"},
    {"id_pieza": 7,  "codigo": "BAT-75AH-007","nombre": "Batería 75Ah 12V",              "stock": 8,  "precio_venta": 380.00, "proveedor": "ElectroParts Peru"},
    {"id_pieza": 8,  "codigo": "AMO-DEL-008", "nombre": "Amortiguador Delantero",        "stock": 4,  "precio_venta": 250.00, "proveedor": "Suspensiones Lima"},
    {"id_pieza": 9,  "codigo": "FIL-COM-009", "nombre": "Filtro de Combustible",         "stock": 1,  "precio_venta": 55.00,  "proveedor": "AutoParts SAC"},
    {"id_pieza": 10, "codigo": "RAD-UNI-010", "nombre": "Radiador Universal",            "stock": 5,  "precio_venta": 450.00, "proveedor": "CoolingParts SAC"},
    {"id_pieza": 11, "codigo": "BOM-AGU-011", "nombre": "Bomba de Agua",                 "stock": 7,  "precio_venta": 180.00, "proveedor": "AutoParts SAC"},
    {"id_pieza": 12, "codigo": "TER-010-012", "nombre": "Termostato",                    "stock": 12, "precio_venta": 40.00,  "proveedor": "AutoParts SAC"},
    {"id_pieza": 13, "codigo": "CAD-DIS-013", "nombre": "Cadena de Distribución",        "stock": 3,  "precio_venta": 320.00, "proveedor": "TransmisionPeru"},
    {"id_pieza": 14, "codigo": "LIQ-FRE-014", "nombre": "Líquido de Frenos DOT4 (1L)",  "stock": 20, "precio_venta": 28.00,  "proveedor": "FrenoPeru EIRL"},
    {"id_pieza": 15, "codigo": "VEL-RUE-015", "nombre": "Sensor de Velocidad de Rueda",  "stock": 6,  "precio_venta": 195.00, "proveedor": "ElectroParts Peru"},
]

# ─────────────────────────────────────────────
# 6. DETALLE_ORDEN_REPUESTOS
# ─────────────────────────────────────────────
DETALLE_ORDEN_REPUESTOS = [
    {"id_detalle": 1, "id_orden": 1, "id_pieza": 1,  "cantidad": 1, "precio_unitario": 35.00},
    {"id_detalle": 2, "id_orden": 1, "id_pieza": 6,  "cantidad": 1, "precio_unitario": 95.00},
    {"id_detalle": 3, "id_orden": 2, "id_pieza": 3,  "cantidad": 1, "precio_unitario": 120.00},
    {"id_detalle": 4, "id_orden": 2, "id_pieza": 14, "cantidad": 2, "precio_unitario": 28.00},
    {"id_detalle": 5, "id_orden": 3, "id_pieza": 8,  "cantidad": 2, "precio_unitario": 250.00},
    {"id_detalle": 6, "id_orden": 4, "id_pieza": 4,  "cantidad": 1, "precio_unitario": 80.00},
    {"id_detalle": 7, "id_orden": 4, "id_pieza": 2,  "cantidad": 1, "precio_unitario": 45.00},
    {"id_detalle": 8, "id_orden": 5, "id_pieza": 7,  "cantidad": 1, "precio_unitario": 380.00},
    {"id_detalle": 9, "id_orden": 8, "id_pieza": 15, "cantidad": 1, "precio_unitario": 195.00},
]

# ─────────────────────────────────────────────
# 7. FACTURAS
# ─────────────────────────────────────────────
FACTURAS = [
    {"id_factura": 1, "id_orden": 1, "fecha": "2026-05-12", "total": 280.00,  "metodo_pago": "Efectivo",       "estado_pago": "pagada"},
    {"id_factura": 2, "id_orden": 2, "fecha": "2026-05-17", "total": 376.00,  "metodo_pago": "Tarjeta Débito", "estado_pago": "pagada"},
    {"id_factura": 3, "id_orden": 3, "fecha": "2026-05-22", "total": 750.00,  "metodo_pago": "Transferencia",  "estado_pago": "pendiente"},
    {"id_factura": 4, "id_orden": 4, "fecha": "2026-05-27", "total": 275.00,  "metodo_pago": "Efectivo",       "estado_pago": "pagada"},
    {"id_factura": 5, "id_orden": 5, "fecha": "2026-06-03", "total": 530.00,  "metodo_pago": "Tarjeta Crédito","estado_pago": "pendiente"},
    {"id_factura": 6, "id_orden": 6, "fecha": "2026-06-07", "total": 180.00,  "metodo_pago": "Efectivo",       "estado_pago": "pendiente"},
    {"id_factura": 7, "id_orden": 7, "fecha": "2026-06-10", "total": 420.00,  "metodo_pago": "Transferencia",  "estado_pago": "pendiente"},
    {"id_factura": 8, "id_orden": 8, "fecha": "2026-06-12", "total": 345.00,  "metodo_pago": "Efectivo",       "estado_pago": "pagada"},
]

# ─────────────────────────────────────────────
# 8. USUARIOS
# ─────────────────────────────────────────────
USUARIOS = [
    {"id_usuario": 1, "id_empleado": 1, "username": "admin",       "password": "admin123",    "rol": "admin",       "estado": "activo"},
    {"id_usuario": 2, "id_empleado": 2, "username": "mecanico1",   "password": "mec2026",     "rol": "mecanico",    "estado": "activo"},
    {"id_usuario": 3, "id_empleado": 4, "username": "facturacion", "password": "fact2026",    "rol": "facturacion", "estado": "activo"},
    {"id_usuario": 4, "id_empleado": 5, "username": "readonly",    "password": "view2026",    "rol": "readonly",    "estado": "activo"},
    {"id_usuario": 5, "id_empleado": 3, "username": "kevin_elec",  "password": "elec2026",    "rol": "mecanico",    "estado": "inactivo"},
]

# ─────────────────────────────────────────────
# Contadores de auto-incremento (simulando SEQUENCES de Oracle)
# ─────────────────────────────────────────────
_counters = {
    "clientes": max(c["id_cliente"] for c in CLIENTES),
    "vehiculos": max(v["id_vehiculo"] for v in VEHICULOS),
    "empleados": max(e["id_empleado"] for e in EMPLEADOS),
    "ordenes": max(o["id_orden"] for o in ORDENES_TRABAJO),
    "repuestos": max(r["id_pieza"] for r in INVENTARIO_REPUESTOS),
    "detalles": max(d["id_detalle"] for d in DETALLE_ORDEN_REPUESTOS),
    "facturas": max(f["id_factura"] for f in FACTURAS),
    "usuarios": max(u["id_usuario"] for u in USUARIOS),
}

def next_id(table: str) -> int:
    """Simula el NEXTVAL de una SEQUENCE Oracle."""
    _counters[table] += 1
    return _counters[table]
