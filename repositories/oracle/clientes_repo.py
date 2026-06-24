"""
repositories/oracle/clientes_repo.py
=====================================
Repositorio para la tabla CLIENTES (Oracle).
Encapsula todas las queries a la entidad Cliente.
"""
from typing import List, Optional, Dict
from database import OracleDB


class ClienteRepository:
    """
    Repositorio de clientes.
    Recibe la instancia de OracleDB (inyección de dependencias).

    TODO (Oracle real): reemplazar cada método por cursor.execute(SQL, params)
    """

    def __init__(self, db: OracleDB):
        self._db = db

    # ── Lectura ───────────────────────────────────────────────────────

    def get_all(self) -> List[Dict]:
        """
        Retorna todos los clientes.
        TODO: cursor.execute("SELECT * FROM CLIENTES ORDER BY nombre")
        """
        return self._db.get_all_clientes()

    def get_by_id(self, id_cliente: int) -> Optional[Dict]:
        """
        Retorna un cliente por PK o None.
        TODO: cursor.execute("SELECT * FROM CLIENTES WHERE id_cliente=:1", [id_cliente])
        """
        return self._db.get_cliente(id_cliente)

    # ── Escritura ─────────────────────────────────────────────────────

    def create(self, nombre: str, telefono: str, dni: str, email: str) -> Dict:
        """
        Inserta un nuevo cliente.
        TODO: cursor.execute("INSERT INTO CLIENTES VALUES(SEQ_CLI.NEXTVAL,:1,:2,:3,:4)", ...)
        """
        return self._db.create_cliente(nombre, telefono, dni, email)

    def update(self, id_cliente: int, nombre: str, telefono: str,
               dni: str, email: str) -> bool:
        """
        Actualiza los datos de un cliente existente.
        TODO: cursor.execute("UPDATE CLIENTES SET nombre=:1,... WHERE id_cliente=:5", ...)
        """
        return self._db.update_cliente(id_cliente, nombre, telefono, dni, email)

    def delete(self, id_cliente: int) -> bool:
        """
        Elimina un cliente por PK.
        TODO: cursor.execute("DELETE FROM CLIENTES WHERE id_cliente=:1", [id_cliente])
        """
        return self._db.delete_cliente(id_cliente)
