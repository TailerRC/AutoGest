"""
mock_data/oracle_data.py
========================
Simulación de las tablas relacionales de Oracle en memoria.
"""

CLIENTES = [
    {"id_cliente": 1, "nombre": "Carlos Mendoza Ríos", "telefono": "987654321", "dni": "45123678", "email": "carlos.mendoza@gmail.com"},
    {"id_cliente": 2, "nombre": "Lucía Fernández Soto", "telefono": "987654322", "dni": "45123679", "email": "lucia.fernandez@gmail.com"},
    {"id_cliente": 3, "nombre": "Jorge Aliaga Paredes", "telefono": "987654323", "dni": "45123680", "email": "jorge.aliaga@gmail.com"},
    {"id_cliente": 4, "nombre": "María Quispe Huamán", "telefono": "987654324", "dni": "45123681", "email": "maria.quispe@gmail.com"},
    {"id_cliente": 5, "nombre": "Andrés Salazar Vega", "telefono": "987654325", "dni": "45123682", "email": "andres.salazar@gmail.com"}
]

VEHICULOS = [
    {"id_vehiculo": 1, "id_cliente": 1, "placa": "ABC-123", "marca": "Toyota", "modelo": "Yaris", "anio": 2018},
    {"id_vehiculo": 2, "id_cliente": 2, "placa": "DEF-456", "marca": "Toyota", "modelo": "Corolla", "anio": 2020},
    {"id_vehiculo": 3, "id_cliente": 3, "placa": "GHI-789", "marca": "Toyota", "modelo": "Hilux", "anio": 2019},
    {"id_vehiculo": 4, "id_cliente": 4, "placa": "JKL-012", "marca": "Nissan", "modelo": "Sentra", "anio": 2017},
    {"id_vehiculo": 5, "id_cliente": 5, "placa": "MNO-345", "marca": "Nissan", "modelo": "Versa", "anio": 2021},
    {"id_vehiculo": 101, "id_cliente": 1, "placa": "PQR-101", "marca": "Toyota", "modelo": "Yaris", "anio": 2018},
    {"id_vehiculo": 104, "id_cliente": 2, "placa": "STU-104", "marca": "Nissan", "modelo": "Sentra", "anio": 2017},
    {"id_vehiculo": 107, "id_cliente": 3, "placa": "VWX-107", "marca": "Honda", "modelo": "Civic", "anio": 2016},
    {"id_vehiculo": 109, "id_cliente": 4, "placa": "YZA-109", "marca": "Hyundai", "modelo": "Elantra", "anio": 2015},
    {"id_vehiculo": 111, "id_cliente": 5, "placa": "BCD-111", "marca": "Kia", "modelo": "Rio", "anio": 2019}
]

EMPLEADOS = [
    {"id_empleado": 1, "nombre": "Pedro Ramírez Castro", "cargo": "Mecánico Senior", "especialidad": "Motor y Transmisión"},
    {"id_empleado": 2, "nombre": "Luis Torres Medina", "cargo": "Mecánico", "especialidad": "Frenos y Suspensión"},
    {"id_empleado": 3, "nombre": "Ana Gómez Rivas", "cargo": "Técnico Electricista", "especialidad": "Sistemas Eléctricos"},
    {"id_empleado": 4, "nombre": "Roberto Flores Díaz", "cargo": "Jefe de Taller", "especialidad": None},
    {"id_empleado": 5, "nombre": "Diego Vargas León", "cargo": "Mecánico", "especialidad": "Diésel"}
]

ORDENES_TRABAJO = [
    {"id_orden": 1, "id_vehiculo": 1, "id_empleado": 1, "fecha_ingreso": "2026-01-10", "fecha_entrega": "2026-01-12", "estado": "completada"},
    {"id_orden": 2, "id_vehiculo": 2, "id_empleado": 2, "fecha_ingreso": "2026-01-12", "fecha_entrega": "2026-01-14", "estado": "completada"},
    {"id_orden": 3, "id_vehiculo": 3, "id_empleado": 3, "fecha_ingreso": "2026-01-15", "fecha_entrega": None, "estado": "en_proceso"},
    {"id_orden": 4, "id_vehiculo": 4, "id_empleado": 1, "fecha_ingreso": "2026-01-18", "fecha_entrega": "2026-01-20", "estado": "completada"},
    {"id_orden": 5, "id_vehiculo": 5, "id_empleado": 5, "fecha_ingreso": "2026-01-20", "fecha_entrega": None, "estado": "pendiente"}
]

INVENTARIO_REPUESTOS = [
    {"id_pieza": 1, "codigo": "REP-FRE-001", "nombre": "Pastillas de Freno Toyota", "stock": 2, "precio_venta": 120.00, "proveedor": "Frenos y Embragues Lima"},
    {"id_pieza": 2, "codigo": "REP-FIL-001", "nombre": "Filtro de Aceite Hyundai", "stock": 1, "precio_venta": 45.00, "proveedor": "Filtros Industriales del Perú"},
    {"id_pieza": 3, "codigo": "REP-BAT-001", "nombre": "Batería 13 Placas Bosch", "stock": 0, "precio_venta": 320.00, "proveedor": "Baterías y Energía Automotriz"},
    {"id_pieza": 4, "codigo": "REP-BUJ-001", "nombre": "Bujías de Iridio NGK", "stock": 8, "precio_venta": 45.00, "proveedor": "Bujías de Iridio Import"},
    {"id_pieza": 5, "codigo": "REP-ACE-001", "nombre": "Aceite Sintético 5W30 Castrol", "stock": 12, "precio_venta": 85.00, "proveedor": "Lubricantes del Pacífico"}
]

DETALLE_ORDEN_REPUESTOS = [
    {"id_detalle": 1, "id_orden": 1, "id_pieza": 1, "cantidad": 1, "precio_unitario": 120.00},
    {"id_detalle": 2, "id_orden": 1, "id_pieza": 2, "cantidad": 1, "precio_unitario": 45.00},
    {"id_detalle": 3, "id_orden": 2, "id_pieza": 4, "cantidad": 4, "precio_unitario": 45.00},
    {"id_detalle": 4, "id_orden": 4, "id_pieza": 5, "cantidad": 2, "precio_unitario": 85.00},
    {"id_detalle": 5, "id_orden": 5, "id_pieza": 3, "cantidad": 1, "precio_unitario": 320.00}
]

FACTURAS = [
    {"id_factura": 1, "id_orden": 1, "fecha": "2026-01-12", "total": 165.00, "metodo_pago": "Efectivo", "estado_pago": "pagada"},
    {"id_factura": 2, "id_orden": 2, "fecha": "2026-01-14", "total": 180.00, "metodo_pago": "Tarjeta Débito", "estado_pago": "pagada"},
    {"id_factura": 3, "id_orden": 4, "fecha": "2026-01-20", "total": 170.00, "metodo_pago": "Transferencia", "estado_pago": "pendiente"},
    {"id_factura": 4, "id_orden": 1, "fecha": "2026-01-13", "total": 50.00, "metodo_pago": "Tarjeta Crédito", "estado_pago": "pagada"},
    {"id_factura": 5, "id_orden": 2, "fecha": "2026-01-15", "total": 95.00, "metodo_pago": "Efectivo", "estado_pago": "pendiente"}
]

# Modifiqué las contraseñas para usar texto plano temporalmente, 
# facilitando el login de prueba con los passwords esperados por auth.py
USUARIOS = [
    {"id_usuario": 1, "id_empleado": 1, "username": "pedro.ramirez", "password": "mec2026", "rol": "mecanico", "estado": "activo"},
    {"id_usuario": 2, "id_empleado": 2, "username": "luis.torres", "password": "fact2026", "rol": "facturacion", "estado": "activo"},
    {"id_usuario": 3, "id_empleado": 3, "username": "ana.gomez", "password": "admin123", "rol": "admin", "estado": "activo"},
    {"id_usuario": 4, "id_empleado": 4, "username": "roberto.flores", "password": "admin123", "rol": "admin", "estado": "activo"},
    {"id_usuario": 5, "id_empleado": 5, "username": "diego.vargas", "password": "view2026", "rol": "readonly", "estado": "inactivo"}
]

def next_id(tabla: str) -> int:
    return 1000
