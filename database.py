"""
database.py
===========
Capa de acceso a datos para AutoGest.
Simula las conexiones a Oracle y MongoDB usando estructuras en memoria.

IMPORTANTE: Los comentarios "TODO" marcan exactamente dónde se reemplazaría
el mock por conexiones reales a cx_Oracle y pymongo.
"""

from mock_data.oracle_data import (
    CLIENTES, VEHICULOS, EMPLEADOS, ORDENES_TRABAJO,
    INVENTARIO_REPUESTOS, DETALLE_ORDEN_REPUESTOS, FACTURAS, USUARIOS,
    next_id
)
from mock_data.mongo_data import (
    CATALOGO_ESPECIFICACIONES, BITACORA_DIAGNOSTICO, HISTORIAL_MANTENIMIENTO,
    COTIZACIONES, PROVEEDORES, ALERTAS_SISTEMA, LOG_ACTIVIDAD,
    next_mongo_id
)
from datetime import datetime
from typing import Optional, List, Dict, Any


# ═══════════════════════════════════════════════════════════════════════
# ORACLE — Simulación de conexión y operaciones relacionales
# ═══════════════════════════════════════════════════════════════════════

class OracleDB:
    """
    Simula una conexión cx_Oracle.
    
    TODO: Reemplazar __init__ con:
        import cx_Oracle
        self.conn = cx_Oracle.connect(
            user=username,
            password=password,
            dsn=cx_Oracle.makedsn(host, port, service_name=service)
        )
        self.cursor = self.conn.cursor()
    """

    def __init__(self):
        # Mock: referencias directas a las listas en memoria
        self.clientes = CLIENTES
        self.vehiculos = VEHICULOS
        self.empleados = EMPLEADOS
        self.ordenes = ORDENES_TRABAJO
        self.repuestos = INVENTARIO_REPUESTOS
        self.detalles = DETALLE_ORDEN_REPUESTOS
        self.facturas = FACTURAS
        self.usuarios = USUARIOS

    # ── CLIENTES ──────────────────────────────────────────────────────
    def get_all_clientes(self) -> List[Dict]:
        # TODO: cursor.execute("SELECT * FROM CLIENTES ORDER BY nombre")
        return list(self.clientes)

    def get_cliente(self, id_cliente: int) -> Optional[Dict]:
        # TODO: cursor.execute("SELECT * FROM CLIENTES WHERE id_cliente=:1", [id_cliente])
        return next((c for c in self.clientes if c["id_cliente"] == id_cliente), None)

    def create_cliente(self, nombre: str, telefono: str, dni: str, email: str) -> Dict:
        # TODO: cursor.execute("INSERT INTO CLIENTES VALUES (SEQ_CLI.NEXTVAL,:1,:2,:3,:4)", ...)
        nuevo = {
            "id_cliente": next_id("clientes"),
            "nombre": nombre, "telefono": telefono,
            "dni": dni, "email": email
        }
        self.clientes.append(nuevo)
        return nuevo

    def update_cliente(self, id_cliente: int, nombre: str, telefono: str, dni: str, email: str) -> bool:
        # TODO: cursor.execute("UPDATE CLIENTES SET nombre=:1,... WHERE id_cliente=:5", ...)
        c = self.get_cliente(id_cliente)
        if not c:
            return False
        c.update({"nombre": nombre, "telefono": telefono, "dni": dni, "email": email})
        return True

    def delete_cliente(self, id_cliente: int) -> bool:
        # TODO: cursor.execute("DELETE FROM CLIENTES WHERE id_cliente=:1", [id_cliente])
        c = self.get_cliente(id_cliente)
        if not c:
            return False
        self.clientes.remove(c)
        return True

    # ── VEHÍCULOS ─────────────────────────────────────────────────────
    def get_all_vehiculos(self) -> List[Dict]:
        # TODO: cursor.execute("SELECT v.*, c.nombre FROM VEHICULOS v JOIN CLIENTES c ON v.id_cliente=c.id_cliente")
        result = []
        for v in self.vehiculos:
            vd = dict(v)
            cliente = self.get_cliente(v["id_cliente"])
            vd["nombre_cliente"] = cliente["nombre"] if cliente else "—"
            result.append(vd)
        return result

    def get_vehiculo(self, id_vehiculo: int) -> Optional[Dict]:
        return next((v for v in self.vehiculos if v["id_vehiculo"] == id_vehiculo), None)

    def create_vehiculo(self, id_cliente: int, placa: str, marca: str, modelo: str, año: int) -> Dict:
        nuevo = {
            "id_vehiculo": next_id("vehiculos"),
            "id_cliente": id_cliente, "placa": placa.upper(),
            "marca": marca, "modelo": modelo, "año": año
        }
        self.vehiculos.append(nuevo)
        return nuevo

    def update_vehiculo(self, id_vehiculo: int, id_cliente: int, placa: str, marca: str, modelo: str, año: int) -> bool:
        v = self.get_vehiculo(id_vehiculo)
        if not v:
            return False
        v.update({"id_cliente": id_cliente, "placa": placa.upper(), "marca": marca, "modelo": modelo, "año": año})
        return True

    def delete_vehiculo(self, id_vehiculo: int) -> bool:
        v = self.get_vehiculo(id_vehiculo)
        if not v:
            return False
        self.vehiculos.remove(v)
        return True

    # ── EMPLEADOS ─────────────────────────────────────────────────────
    def get_all_empleados(self) -> List[Dict]:
        return list(self.empleados)

    def get_empleado(self, id_empleado: int) -> Optional[Dict]:
        return next((e for e in self.empleados if e["id_empleado"] == id_empleado), None)

    def create_empleado(self, nombre: str, cargo: str, especialidad: str) -> Dict:
        nuevo = {
            "id_empleado": next_id("empleados"),
            "nombre": nombre, "cargo": cargo, "especialidad": especialidad
        }
        self.empleados.append(nuevo)
        return nuevo

    def update_empleado(self, id_empleado: int, nombre: str, cargo: str, especialidad: str) -> bool:
        e = self.get_empleado(id_empleado)
        if not e:
            return False
        e.update({"nombre": nombre, "cargo": cargo, "especialidad": especialidad})
        return True

    # ── ÓRDENES DE TRABAJO ────────────────────────────────────────────
    def get_all_ordenes(self) -> List[Dict]:
        result = []
        for o in self.ordenes:
            od = dict(o)
            v = self.get_vehiculo(o["id_vehiculo"])
            e = self.get_empleado(o["id_empleado"])
            od["placa"] = v["placa"] if v else "—"
            od["nombre_empleado"] = e["nombre"] if e else "—"
            if v:
                cliente = self.get_cliente(v["id_cliente"])
                od["nombre_cliente"] = cliente["nombre"] if cliente else "—"
            else:
                od["nombre_cliente"] = "—"
            result.append(od)
        return result

    def get_orden(self, id_orden: int) -> Optional[Dict]:
        return next((o for o in self.ordenes if o["id_orden"] == id_orden), None)

    def get_orden_detallada(self, id_orden: int) -> Optional[Dict]:
        o = self.get_orden(id_orden)
        if not o:
            return None
        od = dict(o)
        v = self.get_vehiculo(o["id_vehiculo"])
        e = self.get_empleado(o["id_empleado"])
        od["vehiculo"] = v
        od["empleado"] = e
        if v:
            od["cliente"] = self.get_cliente(v["id_cliente"])
        else:
            od["cliente"] = None
        od["detalles"] = self.get_detalles_orden(id_orden)
        return od

    def create_orden(self, id_vehiculo: int, id_empleado: int, fecha_ingreso: str, fecha_entrega: str) -> Dict:
        nuevo = {
            "id_orden": next_id("ordenes"),
            "id_vehiculo": id_vehiculo, "id_empleado": id_empleado,
            "fecha_ingreso": fecha_ingreso, "fecha_entrega": fecha_entrega,
            "estado": "pendiente"
        }
        self.ordenes.append(nuevo)
        return nuevo

    def update_orden_estado(self, id_orden: int, estado: str) -> bool:
        o = self.get_orden(id_orden)
        if not o:
            return False
        o["estado"] = estado
        return True

    def update_orden(self, id_orden: int, id_vehiculo: int, id_empleado: int,
                     fecha_ingreso: str, fecha_entrega: str, estado: str) -> bool:
        o = self.get_orden(id_orden)
        if not o:
            return False
        o.update({
            "id_vehiculo": id_vehiculo, "id_empleado": id_empleado,
            "fecha_ingreso": fecha_ingreso, "fecha_entrega": fecha_entrega,
            "estado": estado
        })
        return True

    # ── REPUESTOS ─────────────────────────────────────────────────────
    def get_all_repuestos(self) -> List[Dict]:
        return list(self.repuestos)

    def get_repuesto(self, id_pieza: int) -> Optional[Dict]:
        return next((r for r in self.repuestos if r["id_pieza"] == id_pieza), None)

    def create_repuesto(self, codigo: str, nombre: str, stock: int, precio_venta: float, proveedor: str) -> Dict:
        nuevo = {
            "id_pieza": next_id("repuestos"),
            "codigo": codigo, "nombre": nombre, "stock": stock,
            "precio_venta": precio_venta, "proveedor": proveedor
        }
        self.repuestos.append(nuevo)
        return nuevo

    def update_repuesto(self, id_pieza: int, codigo: str, nombre: str, stock: int,
                        precio_venta: float, proveedor: str) -> bool:
        r = self.get_repuesto(id_pieza)
        if not r:
            return False
        r.update({"codigo": codigo, "nombre": nombre, "stock": stock,
                  "precio_venta": precio_venta, "proveedor": proveedor})
        return True

    def delete_repuesto(self, id_pieza: int) -> bool:
        r = self.get_repuesto(id_pieza)
        if not r:
            return False
        self.repuestos.remove(r)
        return True

    # ── DETALLES ORDEN ────────────────────────────────────────────────
    def get_detalles_orden(self, id_orden: int) -> List[Dict]:
        result = []
        for d in self.detalles:
            if d["id_orden"] == id_orden:
                dd = dict(d)
                r = self.get_repuesto(d["id_pieza"])
                dd["nombre_pieza"] = r["nombre"] if r else "—"
                dd["subtotal"] = dd["cantidad"] * dd["precio_unitario"]
                result.append(dd)
        return result

    def add_detalle_orden(self, id_orden: int, id_pieza: int, cantidad: int, precio_unitario: float) -> Dict:
        nuevo = {
            "id_detalle": next_id("detalles"),
            "id_orden": id_orden, "id_pieza": id_pieza,
            "cantidad": cantidad, "precio_unitario": precio_unitario
        }
        self.detalles.append(nuevo)
        # Descontar stock
        r = self.get_repuesto(id_pieza)
        if r:
            r["stock"] = max(0, r["stock"] - cantidad)
        return nuevo

    # ── FACTURAS ──────────────────────────────────────────────────────
    def get_all_facturas(self) -> List[Dict]:
        result = []
        for f in self.facturas:
            fd = dict(f)
            o = self.get_orden(f["id_orden"])
            if o:
                v = self.get_vehiculo(o["id_vehiculo"])
                if v:
                    c = self.get_cliente(v["id_cliente"])
                    fd["nombre_cliente"] = c["nombre"] if c else "—"
                    fd["placa"] = v["placa"]
                else:
                    fd["nombre_cliente"] = "—"
                    fd["placa"] = "—"
            else:
                fd["nombre_cliente"] = "—"
                fd["placa"] = "—"
            result.append(fd)
        return result

    def get_factura(self, id_factura: int) -> Optional[Dict]:
        return next((f for f in self.facturas if f["id_factura"] == id_factura), None)

    def get_factura_por_orden(self, id_orden: int) -> Optional[Dict]:
        return next((f for f in self.facturas if f["id_orden"] == id_orden), None)

    def create_factura(self, id_orden: int, total: float, metodo_pago: str) -> Dict:
        nuevo = {
            "id_factura": next_id("facturas"),
            "id_orden": id_orden,
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "total": total, "metodo_pago": metodo_pago,
            "estado_pago": "pendiente"
        }
        self.facturas.append(nuevo)
        return nuevo

    def update_factura_estado(self, id_factura: int, estado_pago: str) -> bool:
        f = self.get_factura(id_factura)
        if not f:
            return False
        f["estado_pago"] = estado_pago
        return True

    # ── USUARIOS ──────────────────────────────────────────────────────
    def get_all_usuarios(self) -> List[Dict]:
        result = []
        for u in self.usuarios:
            ud = dict(u)
            e = self.get_empleado(u["id_empleado"])
            ud["nombre_empleado"] = e["nombre"] if e else "—"
            result.append(ud)
        return result

    def get_usuario_by_username(self, username: str) -> Optional[Dict]:
        return next((u for u in self.usuarios if u["username"] == username), None)

    def get_usuario(self, id_usuario: int) -> Optional[Dict]:
        return next((u for u in self.usuarios if u["id_usuario"] == id_usuario), None)

    def create_usuario(self, id_empleado: int, username: str, password: str, rol: str) -> Dict:
        nuevo = {
            "id_usuario": next_id("usuarios"),
            "id_empleado": id_empleado, "username": username,
            "password": password, "rol": rol, "estado": "activo"
        }
        self.usuarios.append(nuevo)
        return nuevo

    def update_usuario(self, id_usuario: int, username: str, rol: str,
                       estado: str, password: Optional[str] = None) -> bool:
        u = self.get_usuario(id_usuario)
        if not u:
            return False
        u.update({"username": username, "rol": rol, "estado": estado})
        if password:
            u["password"] = password
        return True


# ═══════════════════════════════════════════════════════════════════════
# MONGODB — Simulación de conexión y operaciones de documentos
# ═══════════════════════════════════════════════════════════════════════

class MongoDB:
    """
    Simula una conexión pymongo a MongoDB.

    TODO: Reemplazar __init__ con:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["autogest_db"]
        self.catalogo = db["catalogo_especificaciones_tecnicas"]
        self.bitacora = db["bitacora_diagnostico"]
        ...etc
    """

    def __init__(self):
        self.catalogo = CATALOGO_ESPECIFICACIONES
        self.bitacora = BITACORA_DIAGNOSTICO
        self.historial = HISTORIAL_MANTENIMIENTO
        self.cotizaciones = COTIZACIONES
        self.proveedores = PROVEEDORES
        self.alertas = ALERTAS_SISTEMA
        self.logs = LOG_ACTIVIDAD

    # ── CATÁLOGO TÉCNICO ──────────────────────────────────────────────
    def get_all_catalogo(self) -> List[Dict]:
        # TODO: return list(self.catalogo.find())
        return list(self.catalogo)

    def buscar_catalogo(self, marca: str = "", modelo: str = "", año: int = None) -> List[Dict]:
        # TODO: query = {}; if marca: query["marca"] = {"$regex": marca, "$options": "i"}
        result = self.catalogo
        if marca:
            result = [c for c in result if marca.lower() in c["marca"].lower()]
        if modelo:
            result = [c for c in result if modelo.lower() in c["modelo"].lower()]
        if año:
            result = [c for c in result if c["año"] == año]
        return result

    # ── BITÁCORA DE DIAGNÓSTICO ───────────────────────────────────────
    def get_all_bitacoras(self) -> List[Dict]:
        # TODO: return list(self.bitacora.find().sort("fecha", -1))
        return list(self.bitacora)

    def get_bitacora_by_orden(self, id_orden: int) -> Optional[Dict]:
        # TODO: return self.bitacora.find_one({"id_orden_ref": id_orden})
        return next((b for b in self.bitacora if b["id_orden_ref"] == id_orden), None)

    def create_bitacora(self, id_orden: int, mecanico: str, sintomas: List[str],
                        codigos_obd: List[str], hallazgos: str, mano_de_obra: float) -> Dict:
        # TODO: return self.bitacora.insert_one({...}).inserted_id
        nuevo = {
            "_id": next_mongo_id("bitacora"),
            "id_orden_ref": id_orden,
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "mecanico": mecanico,
            "sintomas": sintomas,
            "codigos_obd": codigos_obd,
            "hallazgos": hallazgos,
            "fotos": [],
            "mano_de_obra": mano_de_obra
        }
        self.bitacora.append(nuevo)
        return nuevo

    # ── PROVEEDORES ───────────────────────────────────────────────────
    def get_all_proveedores(self) -> List[Dict]:
        return list(self.proveedores)

    # ── LOG DE ACTIVIDAD ──────────────────────────────────────────────
    def registrar_log(self, id_empleado: int, accion: str, modulo: str, resultado: str) -> None:
        # TODO: self.logs.insert_one({...})
        log = {
            "_id": next_mongo_id("log"),
            "id_empleado": id_empleado,
            "accion": accion,
            "modulo": modulo,
            "fecha_hora": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "resultado": resultado
        }
        self.logs.append(log)

    def get_logs(self, limit: int = 50) -> List[Dict]:
        # TODO: return list(self.logs.find().sort("fecha_hora", -1).limit(limit))
        return list(reversed(self.logs[-limit:]))

    # ── ALERTAS ───────────────────────────────────────────────────────
    def get_alertas_activas(self, destinatario: str = None) -> List[Dict]:
        result = [a for a in self.alertas if a["estado"] == "activa"]
        if destinatario:
            result = [a for a in result if a["destinatario"] == destinatario or a["destinatario"] == "admin"]
        return result


# ═══════════════════════════════════════════════════════════════════════
# Instancias globales (singleton pattern simple)
# ═══════════════════════════════════════════════════════════════════════

def get_oracle_connection() -> OracleDB:
    """
    Retorna la instancia de la capa Oracle.
    
    TODO: Reemplazar por:
        import cx_Oracle
        conn = cx_Oracle.connect(
            user=os.getenv("ORACLE_USER"),
            password=os.getenv("ORACLE_PASSWORD"),
            dsn=cx_Oracle.makedsn(
                os.getenv("ORACLE_HOST", "localhost"),
                os.getenv("ORACLE_PORT", 1521),
                service_name=os.getenv("ORACLE_SERVICE")
            )
        )
        return conn
    """
    return _oracle_instance

def get_mongo_connection() -> MongoDB:
    """
    Retorna la instancia de la capa MongoDB.
    
    TODO: Reemplazar por:
        import pymongo
        client = pymongo.MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
        return client["autogest_db"]
    """
    return _mongo_instance

# Inicializar singletons
_oracle_instance = OracleDB()
_mongo_instance = MongoDB()
