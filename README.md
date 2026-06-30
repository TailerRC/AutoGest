# AutoGest 🔧
### Sistema de Gestión de Taller Mecánico y Concesionaria
**Universidad Ricardo Palma — Curso: Base de Datos II**

---

## Cómo ejecutar

```bash
# 1. Instalar dependencias (ya instaladas si requirements.txt fue procesado)
pip install -r requirements.txt

# 2. Ejecutar la aplicación
python main.py

# 3. Abrir en el navegador
http://localhost:5001
```

---

## Usuarios de prueba

| Username | Contraseña | Rol | Acceso |
|---|---|---|---|
| `admin` | `admin123` | **Admin** | Todo: CRUD completo de todos los módulos |
| `mecanico1` | `mec2026` | **Mecánico** | Órdenes, Repuestos, Catálogo, Bitácora |
| `facturacion` | `fact2026` | **Facturación** | Facturas, Órdenes, Clientes |
| `readonly` | `view2026` | **Solo Lectura** | Reportes, Órdenes, Facturas (solo ver) |

---

## Arquitectura del Sistema

```
AutoGest/
├── main.py                    # FastHTML app + todas las rutas
├── database.py                # Capa de acceso datos (Oracle + MongoDB simulados)
├── auth.py                    # Autenticación, roles y permisos
├── mock_data/
│   ├── oracle_data.py         # 8 tablas Oracle simuladas (listas de dicts)
│   └── mongo_data.py          # 7 colecciones MongoDB simuladas
├── routes/
│   ├── helpers.py             # Layout, badges, componentes reutilizables
│   ├── clientes.py            # CRUD Clientes
│   ├── vehiculos.py           # CRUD Vehículos
│   ├── empleados.py           # CRUD Empleados
│   ├── ordenes.py             # Órdenes de trabajo + repuestos
│   ├── repuestos.py           # Inventario de repuestos
│   ├── facturas.py            # Gestión de facturas
│   ├── usuarios.py            # Gestión de usuarios (solo admin)
│   ├── catalogo_tecnico.py    # Catálogo MongoDB
│   ├── bitacora.py            # Bitácora diagnóstico MongoDB
│   └── reportes.py            # Reporte combinado Oracle + MongoDB
└── static/styles/styles.css   # Diseño dark mode
```

---

## Base de Datos Simulada

### Oracle (8 tablas relacionales)
| Tabla | Descripción |
|---|---|
| CLIENTES | Datos de clientes (10 registros) |
| VEHICULOS | Vehículos vinculados a clientes (10 registros) |
| EMPLEADOS | Personal del taller (5 registros) |
| ORDENES_TRABAJO | Órdenes de servicio (10 registros) |
| INVENTARIO_REPUESTOS | Stock de piezas (15 registros) |
| DETALLE_ORDEN_REPUESTOS | Repuestos por orden (FK) |
| FACTURAS | Facturación de órdenes (8 registros) |
| USUARIOS | Cuentas con roles (5 registros) |

### MongoDB (7 colecciones documentales)
| Colección | Descripción |
|---|---|
| catalogo_especificaciones_tecnicas | Specs técnicas por marca/modelo |
| bitacora_diagnostico | Diagnósticos con arrays de síntomas y códigos OBD |
| historial_mantenimiento_vehiculo | Historial de servicios por placa |
| cotizaciones | Cotizaciones con items embebidos |
| proveedores | Proveedores con productos como array |
| alertas_sistema | Alertas activas del sistema |
| log_actividad | Registro de todas las acciones del sistema |

---

---

## Migración a bases de datos reales

Todos los puntos de migración están marcados con comentarios `# TODO`:

**Oracle real** → buscar en `database.py`:
```python
# TODO: reemplazar con:
# import cx_Oracle
# conn = cx_Oracle.connect(user, password, dsn)
```

**MongoDB real** → buscar en `database.py`:
```python
# TODO: reemplazar con:
# import pymongo
# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client["autogest_db"]
```

Configurar credenciales en `.env`:
```
ORACLE_USER=autogest_user
ORACLE_PASSWORD=tu_password
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE=ORCL
MONGO_URI=mongodb://localhost:27017/
```

---

*Proyecto académico — Base de Datos II — URP 2026*