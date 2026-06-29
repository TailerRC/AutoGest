"""
repositories/mongo/catalogo_repo.py
=====================================
Repositorio para la colección catalogo_especificaciones_tecnicas (MongoDB).
"""
from typing import List, Optional, Dict
from database import MongoDB


class CatalogoRepository:
    """
    Repositorio del catálogo técnico de vehículos.

    TODO (MongoDB real): reemplazar por operaciones pymongo/Motor:
        self._col = db["catalogo_especificaciones_tecnicas"]
        return list(self._col.find())
    """

    def __init__(self, db: MongoDB):
        self._db = db

    def get_all(self) -> List[Dict]:
        """
        TODO: return list(self._col.find().sort("marca", 1))
        """
        return self._db.get_all_catalogo()

    def buscar(self, marca: str = "", modelo: str = "",
               año: Optional[int] = None) -> List[Dict]:
        """
        Búsqueda flexible con filtros opcionales.
        TODO: query = {}
              if marca:  query["marca"]  = {"$regex": marca, "$options": "i"}
              if modelo: query["modelo"] = {"$regex": modelo, "$options": "i"}
              if año:    query["año"]    = año
              return list(self._col.find(query))
        """
        return self._db.buscar_catalogo(marca=marca, modelo=modelo, año=año)

    def actualizar(self, codigo: str, marca: str, modelo: str, anio: int,
                motor: str, aceite: str, transmision: str,
                bujias: str, bateria: str, otros: str = "") -> bool:
        """
        TODO: self._col.update_one({"codigoEspecificacion": codigo}, {"$set": {...}})
        """
        return self._db.update_catalogo(codigo, marca, modelo, anio, motor,
                                        aceite, transmision, bujias, bateria, otros)