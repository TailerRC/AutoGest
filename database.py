"""
database.py
===========
Capa de acceso a datos para AutoGest.
Simula las conexiones a Oracle y MongoDB usando estructuras en memoria.

IMPORTANTE: Los comentarios "TODO" marcan exactamente dónde se reemplazaría
el mock por conexiones reales a cx_Oracle y pymongo.
"""

import os
import oracledb
import pymongo
import uuid
from dotenv import load_dotenv

load_dotenv()

from datetime import datetime
from typing import Optional, List, Dict, Any


# ═══════════════════════════════════════════════════════════════════════
# ORACLE — Simulación de conexión y operaciones relacionales
# ═══════════════════════════════════════════════════════════════════════

class OracleDB:
    """
    Conexión real a Oracle mediante oracledb (modo Thin).
    """

    def __init__(self):
        self.user = os.getenv("ORACLE_USER")
        self.password = os.getenv("ORACLE_PASSWORD")
        self.dsn = os.getenv("ORACLE_DSN")

    def _get_connection(self):
        return oracledb.connect(user=self.user, password=self.password, dsn=self.dsn)

    @staticmethod
    def _rows_to_dicts(cursor) -> List[Dict]:
        columnas = [col[0].lower() for col in cursor.description]
        return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]

    # ── CLIENTES ──────────────────────────────────────────────────────
    def get_all_clientes(self) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_cliente, nombre, telefono, dni, email FROM CLIENTES ORDER BY id_cliente")
        result = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return result

    def get_cliente(self, id_cliente: int) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_cliente, nombre, telefono, dni, email FROM CLIENTES WHERE id_cliente = :1", [id_cliente])
        rows = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return rows[0] if rows else None

    def create_cliente(self, nombre: str, telefono: str, dni: str, email: str) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT NVL(MAX(id_cliente), 0) + 1 FROM CLIENTES")
        nuevo_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO CLIENTES (id_cliente, nombre, telefono, dni, email) VALUES (:1, :2, :3, :4, :5)",
            [nuevo_id, nombre, telefono, dni, email]
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"id_cliente": nuevo_id, "nombre": nombre, "telefono": telefono, "dni": dni, "email": email}

    def update_cliente(self, id_cliente: int, nombre: str, telefono: str, dni: str, email: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE CLIENTES SET nombre=:1, telefono=:2, dni=:3, email=:4 WHERE id_cliente=:5",
            [nombre, telefono, dni, email, id_cliente]
        )
        actualizado = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return actualizado

    def delete_cliente(self, id_cliente: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM CLIENTES WHERE id_cliente = :1", [id_cliente])
        eliminado = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return eliminado

    # ── VEHÍCULOS ─────────────────────────────────────────────────────
    def get_all_vehiculos(self) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.id_vehiculo, v.id_cliente, v.placa, v.marca, v.modelo, v.anio,
                   c.nombre AS nombre_cliente
            FROM VEHICULOS v
            JOIN CLIENTES c ON v.id_cliente = c.id_cliente
            ORDER BY v.id_vehiculo
        """)
        result = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return result

    def get_vehiculo(self, id_vehiculo: int) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_vehiculo, id_cliente, placa, marca, modelo, anio FROM VEHICULOS WHERE id_vehiculo = :1", [id_vehiculo])
        rows = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return rows[0] if rows else None

    def create_vehiculo(self, id_cliente: int, placa: str, marca: str, modelo: str, año: int) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT NVL(MAX(id_vehiculo), 0) + 1 FROM VEHICULOS")
        nuevo_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO VEHICULOS (id_vehiculo, id_cliente, placa, marca, modelo, anio) VALUES (:1, :2, :3, :4, :5, :6)",
            [nuevo_id, id_cliente, placa.upper(), marca, modelo, año]
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"id_vehiculo": nuevo_id, "id_cliente": id_cliente, "placa": placa.upper(), "marca": marca, "modelo": modelo, "año": año}

    def update_vehiculo(self, id_vehiculo: int, id_cliente: int, placa: str, marca: str, modelo: str, año: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE VEHICULOS SET id_cliente=:1, placa=:2, marca=:3, modelo=:4, anio=:5 WHERE id_vehiculo=:6",
            [id_cliente, placa.upper(), marca, modelo, año, id_vehiculo]
        )
        actualizado = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return actualizado

    def delete_vehiculo(self, id_vehiculo: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM VEHICULOS WHERE id_vehiculo = :1", [id_vehiculo])
        eliminado = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return eliminado

    # ── EMPLEADOS ─────────────────────────────────────────────────────
    def get_all_empleados(self) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_empleado, nombre, cargo, especialidad FROM EMPLEADOS ORDER BY id_empleado")
        result = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return result

    def get_empleado(self, id_empleado: int) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_empleado, nombre, cargo, especialidad FROM EMPLEADOS WHERE id_empleado = :1", [id_empleado])
        rows = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return rows[0] if rows else None

    def create_empleado(self, nombre: str, cargo: str, especialidad: str) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT NVL(MAX(id_empleado), 0) + 1 FROM EMPLEADOS")
        nuevo_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO EMPLEADOS (id_empleado, nombre, cargo, especialidad) VALUES (:1, :2, :3, :4)",
            [nuevo_id, nombre, cargo, especialidad]
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"id_empleado": nuevo_id, "nombre": nombre, "cargo": cargo, "especialidad": especialidad}

    def update_empleado(self, id_empleado: int, nombre: str, cargo: str, especialidad: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE EMPLEADOS SET nombre=:1, cargo=:2, especialidad=:3 WHERE id_empleado=:4",
            [nombre, cargo, especialidad, id_empleado]
        )
        actualizado = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return actualizado

    # ── ÓRDENES DE TRABAJO ────────────────────────────────────────────
    def get_all_ordenes(self) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id_orden, o.id_vehiculo, o.id_empleado, o.fecha_ingreso,
                   o.fecha_entrega, o.estado,
                   v.placa, e.nombre AS nombre_empleado, c.nombre AS nombre_cliente
            FROM ORDENES_TRABAJO o
            JOIN VEHICULOS v ON o.id_vehiculo = v.id_vehiculo
            JOIN EMPLEADOS e ON o.id_empleado = e.id_empleado
            JOIN CLIENTES c ON v.id_cliente = c.id_cliente
            ORDER BY o.id_orden DESC
        """)
        result = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return result

    def get_orden(self, id_orden: int) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_orden, id_vehiculo, id_empleado, fecha_ingreso, fecha_entrega, estado FROM ORDENES_TRABAJO WHERE id_orden = :1",
            [id_orden]
        )
        rows = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return rows[0] if rows else None

    def get_orden_detallada(self, id_orden: int) -> Optional[Dict]:
        o = self.get_orden(id_orden)
        if not o:
            return None
        od = dict(o)
        v = self.get_vehiculo(o["id_vehiculo"])
        e = self.get_empleado(o["id_empleado"])
        od["vehiculo"] = v
        od["empleado"] = e
        od["cliente"] = self.get_cliente(v["id_cliente"]) if v else None
        od["detalles"] = self.get_detalles_orden(id_orden)
        return od

    def create_orden(self, id_vehiculo: int, id_empleado: int, fecha_ingreso: str, fecha_entrega: str) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT NVL(MAX(id_orden), 0) + 1 FROM ORDENES_TRABAJO")
        nuevo_id = cursor.fetchone()[0]
        cursor.execute(
            """INSERT INTO ORDENES_TRABAJO (id_orden, id_vehiculo, id_empleado, fecha_ingreso, fecha_entrega, estado)
               VALUES (:1, :2, :3, TO_DATE(:4, 'YYYY-MM-DD'), TO_DATE(:5, 'YYYY-MM-DD'), :6)""",
            [nuevo_id, id_vehiculo, id_empleado, fecha_ingreso, fecha_entrega, "pendiente"]
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"id_orden": nuevo_id, "id_vehiculo": id_vehiculo, "id_empleado": id_empleado,
                "fecha_ingreso": fecha_ingreso, "fecha_entrega": fecha_entrega, "estado": "pendiente"}

    def update_orden_estado(self, id_orden: int, estado: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE ORDENES_TRABAJO SET estado = :1 WHERE id_orden = :2", [estado, id_orden])
        actualizado = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return actualizado

    def update_orden(self, id_orden: int, id_vehiculo: int, id_empleado: int,
                     fecha_ingreso: str, fecha_entrega: str, estado: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE ORDENES_TRABAJO
               SET id_vehiculo=:1, id_empleado=:2, fecha_ingreso=TO_DATE(:3,'YYYY-MM-DD'),
                   fecha_entrega=TO_DATE(:4,'YYYY-MM-DD'), estado=:5
               WHERE id_orden=:6""",
            [id_vehiculo, id_empleado, fecha_ingreso, fecha_entrega, estado, id_orden]
        )
        actualizado = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return actualizado

    # ── REPUESTOS ─────────────────────────────────────────────────────
    def get_all_repuestos(self) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_pieza, codigo, nombre, stock, precio_venta, proveedor FROM INVENTARIO_REPUESTOS ORDER BY nombre")
        result = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return result

    def get_repuesto(self, id_pieza: int) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_pieza, codigo, nombre, stock, precio_venta, proveedor FROM INVENTARIO_REPUESTOS WHERE id_pieza = :1", [id_pieza])
        rows = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return rows[0] if rows else None

    def create_repuesto(self, codigo: str, nombre: str, stock: int, precio_venta: float, proveedor: str) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT NVL(MAX(id_pieza), 0) + 1 FROM INVENTARIO_REPUESTOS")
        nuevo_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO INVENTARIO_REPUESTOS (id_pieza, codigo, nombre, stock, precio_venta, proveedor) VALUES (:1, :2, :3, :4, :5, :6)",
            [nuevo_id, codigo, nombre, stock, precio_venta, proveedor]
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"id_pieza": nuevo_id, "codigo": codigo, "nombre": nombre, "stock": stock,
                "precio_venta": precio_venta, "proveedor": proveedor}

    def update_repuesto(self, id_pieza: int, codigo: str, nombre: str, stock: int,
                        precio_venta: float, proveedor: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE INVENTARIO_REPUESTOS SET codigo=:1, nombre=:2, stock=:3, precio_venta=:4, proveedor=:5 WHERE id_pieza=:6",
            [codigo, nombre, stock, precio_venta, proveedor, id_pieza]
        )
        actualizado = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return actualizado

    def delete_repuesto(self, id_pieza: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM INVENTARIO_REPUESTOS WHERE id_pieza = :1", [id_pieza])
        eliminado = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return eliminado

    # ── DETALLES ORDEN ────────────────────────────────────────────────
    def get_detalles_orden(self, id_orden: int) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.id_detalle, d.id_orden, d.id_pieza, d.cantidad, d.precio_unitario,
                   r.nombre AS nombre_pieza,
                   (d.cantidad * d.precio_unitario) AS subtotal
            FROM DETALLE_ORDEN_REPUESTOS d
            JOIN INVENTARIO_REPUESTOS r ON d.id_pieza = r.id_pieza
            WHERE d.id_orden = :1
        """, [id_orden])
        result = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return result

    def add_detalle_orden(self, id_orden: int, id_pieza: int, cantidad: int, precio_unitario: float) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT NVL(MAX(id_detalle), 0) + 1 FROM DETALLE_ORDEN_REPUESTOS")
        nuevo_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO DETALLE_ORDEN_REPUESTOS (id_detalle, id_orden, id_pieza, cantidad, precio_unitario) VALUES (:1, :2, :3, :4, :5)",
            [nuevo_id, id_orden, id_pieza, cantidad, precio_unitario]
        )
        # Descontar stock (igual que hacía el mock)
        cursor.execute(
            "UPDATE INVENTARIO_REPUESTOS SET stock = GREATEST(stock - :1, 0) WHERE id_pieza = :2",
            [cantidad, id_pieza]
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"id_detalle": nuevo_id, "id_orden": id_orden, "id_pieza": id_pieza,
                "cantidad": cantidad, "precio_unitario": precio_unitario}

    # ── FACTURAS ──────────────────────────────────────────────────────
    def get_all_facturas(self) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.id_factura, f.id_orden, f.fecha, f.total, f.metodo_pago, f.estado_pago,
                   c.nombre AS nombre_cliente, v.placa
            FROM FACTURAS f
            JOIN ORDENES_TRABAJO o ON f.id_orden = o.id_orden
            JOIN VEHICULOS v ON o.id_vehiculo = v.id_vehiculo
            JOIN CLIENTES c ON v.id_cliente = c.id_cliente
            ORDER BY f.id_factura DESC
        """)
        result = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return result

    def get_factura(self, id_factura: int) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_factura, id_orden, fecha, total, metodo_pago, estado_pago FROM FACTURAS WHERE id_factura = :1",
            [id_factura]
        )
        rows = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return rows[0] if rows else None

    def get_factura_por_orden(self, id_orden: int) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_factura, id_orden, fecha, total, metodo_pago, estado_pago FROM FACTURAS WHERE id_orden = :1",
            [id_orden]
        )
        rows = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return rows[0] if rows else None

    def create_factura(self, id_orden: int, total: float, metodo_pago: str) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT NVL(MAX(id_factura), 0) + 1 FROM FACTURAS")
        nuevo_id = cursor.fetchone()[0]
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            """INSERT INTO FACTURAS (id_factura, id_orden, fecha, total, metodo_pago, estado_pago)
               VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'), :4, :5, :6)""",
            [nuevo_id, id_orden, fecha_hoy, total, metodo_pago, "pendiente"]
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"id_factura": nuevo_id, "id_orden": id_orden, "fecha": fecha_hoy,
                "total": total, "metodo_pago": metodo_pago, "estado_pago": "pendiente"}

    def update_factura_estado(self, id_factura: int, estado_pago: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE FACTURAS SET estado_pago = :1 WHERE id_factura = :2", [estado_pago, id_factura])
        actualizado = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return actualizado

    # ── USUARIOS ──────────────────────────────────────────────────────
    def get_all_usuarios(self) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id_usuario, u.id_empleado, u.username, u.rol, u.estado,
                   e.nombre AS nombre_empleado
            FROM USUARIOS u
            JOIN EMPLEADOS e ON u.id_empleado = e.id_empleado
            ORDER BY u.id_usuario
        """)
        result = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return result

    def get_usuario_by_username(self, username: str) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_usuario, id_empleado, username, password, rol, estado FROM USUARIOS WHERE username = :1",
            [username]
        )
        rows = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return rows[0] if rows else None

    def get_usuario(self, id_usuario: int) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_usuario, id_empleado, username, password, rol, estado FROM USUARIOS WHERE id_usuario = :1",
            [id_usuario]
        )
        rows = self._rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return rows[0] if rows else None

    def create_usuario(self, id_empleado: int, username: str, password: str, rol: str) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT NVL(MAX(id_usuario), 0) + 1 FROM USUARIOS")
        nuevo_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO USUARIOS (id_usuario, id_empleado, username, password, rol, estado) VALUES (:1, :2, :3, :4, :5, :6)",
            [nuevo_id, id_empleado, username, password, rol, "activo"]
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"id_usuario": nuevo_id, "id_empleado": id_empleado, "username": username,
                "password": password, "rol": rol, "estado": "activo"}

    def update_usuario(self, id_usuario: int, username: str, rol: str,
                       estado: str, password: Optional[str] = None) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        if password:
            cursor.execute(
                "UPDATE USUARIOS SET username=:1, rol=:2, estado=:3, password=:4 WHERE id_usuario=:5",
                [username, rol, estado, password, id_usuario]
            )
        else:
            cursor.execute(
                "UPDATE USUARIOS SET username=:1, rol=:2, estado=:3 WHERE id_usuario=:4",
                [username, rol, estado, id_usuario]
            )
        actualizado = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return actualizado


# ═══════════════════════════════════════════════════════════════════════
# MONGODB — Simulación de conexión y operaciones de documentos
# ═══════════════════════════════════════════════════════════════════════

class MongoDB:
    """
    Conexión real a MongoDB usando pymongo.
    """

    def __init__(self):
        uri = os.getenv("MONGO_URI")
        db_name = os.getenv("MONGO_DB_NAME", "AutoGest_DB")
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[db_name]
        
        self.catalogo = self.db["catalogo_especificaciones_tecnicas"]
        self.bitacora = self.db["bitacora_diagnostico"]
        self.historial = self.db["historial_mantenimiento"]
        self.cotizaciones = self.db["cotizaciones"]
        self.proveedores = self.db["proveedores"]
        self.alertas = self.db["alertas_sistema"]
        self.logs = self.db["log_actividad"]

    def _remove_id(self, docs):
        """Elimina/convierte el campo '_id' nativo de MongoDB para mantener compatibilidad."""
        res = []
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            res.append(doc)
        return res

    def _remove_id_single(self, doc):
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    # ── CATÁLOGO TÉCNICO ──────────────────────────────────────────────
    def get_all_catalogo(self) -> List[Dict]:
        return self._remove_id(list(self.catalogo.find()))

    def buscar_catalogo(self, marca: str = "", modelo: str = "", año: int = None) -> List[Dict]:
        query = {}
        if marca:
            query["marca"] = {"$regex": marca, "$options": "i"}
        if modelo:
            query["modelo"] = {"$regex": modelo, "$options": "i"}
        if año:
            query["anio"] = año
        return self._remove_id(list(self.catalogo.find(query)))

    # ── BITÁCORA DE DIAGNÓSTICO ───────────────────────────────────────
    def get_all_bitacoras(self) -> List[Dict]:
        # Ordenar si existe campo fecha (o por _id inverso)
        return self._remove_id(list(self.bitacora.find().sort("_id", -1)))

    def get_bitacora_by_vehiculo(self, id_vehiculo: int) -> Optional[Dict]:
        return self._remove_id_single(self.bitacora.find_one({"idVehiculo": id_vehiculo}))

    def create_bitacora(self, id_vehiculo: int, id_empleado: int, codigo_especificacion: str,
                        sintomas: List[str], codigos_obd: List[str], observaciones: str) -> Dict:
        nuevo = {
            "codigoDiagnostico": str(uuid.uuid4()),
            "idVehiculo": id_vehiculo,
            "idEmpleado": id_empleado,
            "codigoEspecificacion": codigo_especificacion,
            "sintomas": sintomas,
            "codigo_OBD": codigos_obd,
            "fotografias_url": [],
            "observaciones": observaciones,
            "fecha": datetime.now()
        }
        self.bitacora.insert_one(nuevo)
        return self._remove_id_single(nuevo)

    # ── HISTORIAL DE MANTENIMIENTO ────────────────────────────────────
    def get_all_historial(self) -> List[Dict]:
        return self._remove_id(list(self.historial.find()))

    def get_historial_by_vehiculo(self, id_vehiculo: int) -> Optional[Dict]:
        return self._remove_id_single(self.historial.find_one({"idVehiculo": id_vehiculo}))

    # ── COTIZACIONES ──────────────────────────────────────────────────
    def get_all_cotizaciones(self) -> List[Dict]:
        return self._remove_id(list(self.cotizaciones.find()))

    def get_cotizacion(self, codigo: str) -> Optional[Dict]:
        return self._remove_id_single(self.cotizaciones.find_one({"codigoCotizacion": codigo}))

    # ── PROVEEDORES ───────────────────────────────────────────────────
    def get_all_proveedores(self) -> List[Dict]:
        return self._remove_id(list(self.proveedores.find()))

    def get_proveedor(self, codigo: str) -> Optional[Dict]:
        return self._remove_id_single(self.proveedores.find_one({"codigoProveedor": codigo}))

    # ── LOG DE ACTIVIDAD ──────────────────────────────────────────────
    def registrar_log(self, id_empleado: int, accion: str, modulo: str, resultado: str) -> None:
        log = {
            "_id": str(uuid.uuid4()),
            "id_empleado": id_empleado,
            "accion": accion,
            "modulo": modulo,
            "fecha_hora": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "resultado": resultado
        }
        self.logs.insert_one(log)

    def get_logs(self, limit: int = 50) -> List[Dict]:
        return self._remove_id(list(self.logs.find().sort("fecha_hora", -1).limit(limit)))

    # ── ALERTAS ───────────────────────────────────────────────────────
    def get_alertas_activas(self, destinatario: str = None) -> List[Dict]:
        query = {}
        if destinatario:
            query["destinatario"] = destinatario
        return self._remove_id(list(self.alertas.find(query)))


# ═══════════════════════════════════════════════════════════════════════
# Instancias globales (singleton pattern simple)
# ═══════════════════════════════════════════════════════════════════════

def get_oracle_connection() -> OracleDB:
    """Retorna la instancia de la capa Oracle (conexión real vía oracledb)."""
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
