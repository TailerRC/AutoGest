"""
mock_data/mongo_data.py
========================
Simula las 7 colecciones de MongoDB como listas de diccionarios Python.
Los documentos incluyen campos embebidos y arrays, tal como en MongoDB real.

TODO: Para migrar a MongoDB real, reemplazar estas estructuras por:
      import pymongo
      client = pymongo.MongoClient("mongodb://localhost:27017/")
      db = client["autogest_db"]
      collection = db["catalogo_especificaciones_tecnicas"]
"""

from datetime import datetime

# ─────────────────────────────────────────────
# 1. catalogo_especificaciones_tecnicas
# ─────────────────────────────────────────────
CATALOGO_ESPECIFICACIONES = [
    {
        "_id": "esp001",
        "marca": "Toyota", "modelo": "Corolla", "año": 2019,
        "tipo_motor": "1.8L 4 Cilindros DOHC",
        "tipo_aceite": "5W-30 Sintético",
        "capacidad_aceite_L": 4.2,
        "presion_neumaticos": {"delantera": "32 PSI", "trasera": "30 PSI"},
        "tipo_frenos": {"delantero": "Disco Ventilado", "trasero": "Disco Sólido"},
        "notas_tecnicas": [
            "Cambio de aceite cada 5,000 km o 6 meses",
            "Revisar tensión de correa a las 60,000 km",
            "Purga de frenos cada 2 años"
        ]
    },
    {
        "_id": "esp002",
        "marca": "Hyundai", "modelo": "Accent", "año": 2020,
        "tipo_motor": "1.4L 4 Cilindros MPI",
        "tipo_aceite": "5W-20 Semi-sintético",
        "capacidad_aceite_L": 3.3,
        "presion_neumaticos": {"delantera": "30 PSI", "trasera": "30 PSI"},
        "tipo_frenos": {"delantero": "Disco Ventilado", "trasero": "Tambor"},
        "notas_tecnicas": [
            "Cambio de aceite cada 7,500 km",
            "Filtro de aire cada 30,000 km",
            "Verificar nivel de líquido refrigerante mensualmente"
        ]
    },
    {
        "_id": "esp003",
        "marca": "Kia", "modelo": "Rio", "año": 2018,
        "tipo_motor": "1.4L 4 Cilindros DOHC",
        "tipo_aceite": "5W-30 Semi-sintético",
        "capacidad_aceite_L": 3.5,
        "presion_neumaticos": {"delantera": "31 PSI", "trasera": "31 PSI"},
        "tipo_frenos": {"delantero": "Disco Ventilado", "trasero": "Tambor"},
        "notas_tecnicas": [
            "Cambio de bujías cada 30,000 km",
            "Revisar zapatas traseras anualmente",
            "Aceite caja automática cada 60,000 km"
        ]
    },
    {
        "_id": "esp004",
        "marca": "Honda", "modelo": "Civic", "año": 2020,
        "tipo_motor": "1.5L Turbo 4 Cilindros DOHC",
        "tipo_aceite": "0W-20 Sintético Total",
        "capacidad_aceite_L": 3.7,
        "presion_neumaticos": {"delantera": "33 PSI", "trasera": "33 PSI"},
        "tipo_frenos": {"delantero": "Disco Ventilado", "trasero": "Disco Sólido"},
        "notas_tecnicas": [
            "Aceite sintético obligatorio por motor turbo",
            "Revisar intercooler cada 40,000 km",
            "Sistema de frenos electrónico, requiere escáner para ajuste"
        ]
    },
    {
        "_id": "esp005",
        "marca": "Kia", "modelo": "Sportage", "año": 2023,
        "tipo_motor": "2.0L 4 Cilindros MPI",
        "tipo_aceite": "5W-30 Sintético",
        "capacidad_aceite_L": 4.5,
        "presion_neumaticos": {"delantera": "35 PSI", "trasera": "35 PSI"},
        "tipo_frenos": {"delantero": "Disco Ventilado", "trasero": "Disco Ventilado"},
        "notas_tecnicas": [
            "Tracción 4WD, revisar diferencial trasero cada 40,000 km",
            "Cambio de aceite de transmisión cada 80,000 km",
            "Sistema ADAS requiere calibración tras cambio de parabrisas"
        ]
    },
]

# ─────────────────────────────────────────────
# 2. bitacora_diagnostico
# ─────────────────────────────────────────────
BITACORA_DIAGNOSTICO = [
    {
        "_id": "bit001",
        "id_orden_ref": 1,
        "fecha": "2026-05-10",
        "mecanico": "Marco Ticona Huayta",
        "sintomas": ["Ruido al frenar", "Vibración en volante a alta velocidad"],
        "codigos_obd": ["C0031", "C0034"],
        "hallazgos": "Pastillas de freno desgastadas al límite. Discos con ranuras. Se recomendó cambio inmediato.",
        "fotos": ["diagnostico_1a.jpg", "diagnostico_1b.jpg"],
        "mano_de_obra": 150.00
    },
    {
        "_id": "bit002",
        "id_orden_ref": 2,
        "fecha": "2026-05-15",
        "mecanico": "Kevin Soto Bernales",
        "sintomas": ["Motor hesitación al acelerar", "Luz de check engine encendida"],
        "codigos_obd": ["P0300", "P0302"],
        "hallazgos": "Fallo en cilindro 2 por bujías defectuosas y bobina de encendido débil. Reemplazar bujías y limpiar inyectores.",
        "fotos": ["diagnostico_2a.jpg"],
        "mano_de_obra": 120.00
    },
    {
        "_id": "bit003",
        "id_orden_ref": 3,
        "fecha": "2026-05-20",
        "mecanico": "Raúl Ponce Delgado",
        "sintomas": ["Golpeteo en suspensión delantera", "Desviación al frenar"],
        "codigos_obd": [],
        "hallazgos": "Amortiguadores delanteros vencidos. Terminales de dirección con juego excesivo. Alineación y balanceo requeridos.",
        "fotos": ["diagnostico_3a.jpg", "diagnostico_3b.jpg", "diagnostico_3c.jpg"],
        "mano_de_obra": 200.00
    },
    {
        "_id": "bit004",
        "id_orden_ref": 4,
        "fecha": "2026-05-25",
        "mecanico": "Marco Ticona Huayta",
        "sintomas": ["Mantenimiento preventivo programado"],
        "codigos_obd": [],
        "hallazgos": "Vehículo en buen estado general. Se realizó cambio de aceite, filtros y revisión de 100 puntos.",
        "fotos": [],
        "mano_de_obra": 100.00
    },
    {
        "_id": "bit005",
        "id_orden_ref": 5,
        "fecha": "2026-06-01",
        "mecanico": "Kevin Soto Bernales",
        "sintomas": ["Vehículo no enciende", "Luces intermitentes al intentar arrancar"],
        "codigos_obd": ["B1000", "P0562"],
        "hallazgos": "Batería sulfatada con 4 años de uso. Alternador verificado como funcional. Bornes con corrosión avanzada.",
        "fotos": ["diagnostico_5a.jpg"],
        "mano_de_obra": 80.00
    },
    {
        "_id": "bit006",
        "id_orden_ref": 8,
        "fecha": "2026-06-10",
        "mecanico": "Kevin Soto Bernales",
        "sintomas": ["ABS activado en condiciones normales", "Luz ABS encendida"],
        "codigos_obd": ["C0031", "C0040"],
        "hallazgos": "Sensor de velocidad de rueda trasera izquierda defectuoso. Anillo tónico con daño mecánico.",
        "fotos": ["diagnostico_6a.jpg", "diagnostico_6b.jpg"],
        "mano_de_obra": 110.00
    },
]

# ─────────────────────────────────────────────
# 3. historial_mantenimiento_vehiculo
# ─────────────────────────────────────────────
HISTORIAL_MANTENIMIENTO = [
    {
        "_id": "hist001",
        "placa": "ABC-123",
        "vin": "JTDBR32E390123456",
        "servicios_anteriores": [
            {"fecha": "2025-11-10", "servicio": "Cambio de aceite y filtros", "km": 45000, "taller": "AutoGest"},
            {"fecha": "2026-05-12", "servicio": "Cambio de pastillas y revisión frenos", "km": 52000, "taller": "AutoGest"},
        ],
        "proxima_revision": "2026-11-12",
        "alertas": ["Próximo cambio de aceite a los 57,000 km"]
    },
    {
        "_id": "hist002",
        "placa": "GHI-789",
        "vin": "KNADN4A37A6234567",
        "servicios_anteriores": [
            {"fecha": "2025-08-15", "servicio": "Cambio de bujías y filtro de aire", "km": 72000, "taller": "AutoGest"},
            {"fecha": "2026-05-17", "servicio": "Reparación sistema eléctrico", "km": 80000, "taller": "AutoGest"},
        ],
        "proxima_revision": "2026-11-17",
        "alertas": ["Revisar correa de distribución a las 90,000 km", "Cambio de aceite pendiente"]
    },
]

# ─────────────────────────────────────────────
# 4. cotizaciones
# ─────────────────────────────────────────────
COTIZACIONES = [
    {
        "_id": "cot001",
        "id_cliente_ref": 3,
        "id_vehiculo_ref": 3,
        "fecha": "2026-06-14",
        "servicios": [
            {"nombre": "Alineación y balanceo", "precio": 80.00},
            {"nombre": "Cambio de aceite", "precio": 150.00},
        ],
        "repuestos": [
            {"nombre": "Aceite Motor 5W-30 (4L)", "cantidad": 1, "precio": 95.00},
            {"nombre": "Filtro de Aceite", "cantidad": 1, "precio": 35.00},
        ],
        "total": 360.00,
        "estado": "pendiente"
    },
    {
        "_id": "cot002",
        "id_cliente_ref": 7,
        "id_vehiculo_ref": 7,
        "fecha": "2026-06-16",
        "servicios": [
            {"nombre": "Diagnóstico eléctrico", "precio": 120.00},
        ],
        "repuestos": [
            {"nombre": "Batería 75Ah 12V", "cantidad": 1, "precio": 380.00},
        ],
        "total": 500.00,
        "estado": "aprobada"
    },
]

# ─────────────────────────────────────────────
# 5. proveedores
# ─────────────────────────────────────────────
PROVEEDORES = [
    {
        "_id": "prov001",
        "nombre": "AutoParts SAC",
        "ruc": "20512345678",
        "contacto": {"nombre": "Juan Pérez", "telefono": "01-234-5678", "email": "ventas@autoparts.pe"},
        "productos": ["Filtros de aceite", "Filtros de aire", "Correas", "Termostatos", "Bombas de agua", "Filtros de combustible"],
        "tiempo_entrega": "24 horas",
        "calificacion": 4.5
    },
    {
        "_id": "prov002",
        "nombre": "ElectroParts Peru",
        "ruc": "20623456789",
        "contacto": {"nombre": "María López", "telefono": "01-345-6789", "email": "info@electroparts.pe"},
        "productos": ["Baterías", "Alternadores", "Sensores", "Módulos ECU"],
        "tiempo_entrega": "48 horas",
        "calificacion": 4.2
    },
    {
        "_id": "prov003",
        "nombre": "FrenoPeru EIRL",
        "ruc": "20734567890",
        "contacto": {"nombre": "Carlos Ruiz", "telefono": "01-456-7890", "email": "pedidos@frenoperu.pe"},
        "productos": ["Pastillas de freno", "Zapatas", "Discos", "Líquido de frenos", "Cilindros"],
        "tiempo_entrega": "24 horas",
        "calificacion": 4.8
    },
]

# ─────────────────────────────────────────────
# 6. alertas_sistema
# ─────────────────────────────────────────────
ALERTAS_SISTEMA = [
    {
        "_id": "alr001",
        "tipo": "stock_bajo",
        "descripcion": "Stock crítico: Filtro de Combustible (1 unidad restante)",
        "fecha": "2026-06-15T08:00:00",
        "prioridad": "alta",
        "estado": "activa",
        "destinatario": "admin"
    },
    {
        "_id": "alr002",
        "tipo": "stock_bajo",
        "descripcion": "Stock bajo: Correa de Alternador (2 unidades restantes)",
        "fecha": "2026-06-15T08:05:00",
        "prioridad": "media",
        "estado": "activa",
        "destinatario": "admin"
    },
    {
        "_id": "alr003",
        "tipo": "orden_vencida",
        "descripcion": "Orden #6 lleva más de 3 días en estado 'pendiente'",
        "fecha": "2026-06-15T09:00:00",
        "prioridad": "media",
        "estado": "activa",
        "destinatario": "mecanico1"
    },
    {
        "_id": "alr004",
        "tipo": "factura_pendiente",
        "descripcion": "Factura #5 pendiente de cobro por S/. 530.00",
        "fecha": "2026-06-10T10:00:00",
        "prioridad": "alta",
        "estado": "activa",
        "destinatario": "facturacion"
    },
]

# ─────────────────────────────────────────────
# 7. log_actividad
# ─────────────────────────────────────────────
LOG_ACTIVIDAD = [
    {
        "_id": "log001",
        "id_empleado": 1,
        "accion": "LOGIN",
        "modulo": "auth",
        "fecha_hora": "2026-06-17T08:00:00",
        "resultado": "exitoso"
    },
    {
        "_id": "log002",
        "id_empleado": 2,
        "accion": "LOGIN",
        "modulo": "auth",
        "fecha_hora": "2026-06-17T08:15:00",
        "resultado": "exitoso"
    },
    {
        "_id": "log003",
        "id_empleado": 2,
        "accion": "CREAR",
        "modulo": "bitacora",
        "fecha_hora": "2026-06-17T08:30:00",
        "resultado": "exitoso"
    },
    {
        "_id": "log004",
        "id_empleado": 3,
        "accion": "INTENTO_SIN_PERMISO",
        "modulo": "usuarios",
        "fecha_hora": "2026-06-17T09:00:00",
        "resultado": "denegado"
    },
    {
        "_id": "log005",
        "id_empleado": 1,
        "accion": "CREAR",
        "modulo": "clientes",
        "fecha_hora": "2026-06-17T09:30:00",
        "resultado": "exitoso"
    },
]

# ─────────────────────────────────────────────
# Contador de IDs para documentos MongoDB
# (simulando ObjectId auto-generado)
# ─────────────────────────────────────────────
_mongo_counters = {
    "bitacora": len(BITACORA_DIAGNOSTICO),
    "log": len(LOG_ACTIVIDAD),
    "cotizaciones": len(COTIZACIONES),
    "alertas": len(ALERTAS_SISTEMA),
}

def next_mongo_id(collection: str) -> str:
    """Genera un ID string simple para documentos MongoDB simulados."""
    _mongo_counters[collection] = _mongo_counters.get(collection, 0) + 1
    return f"{collection}{_mongo_counters[collection]:03d}"
