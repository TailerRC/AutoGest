"""
repositories/mongo/cotizaciones_repo.py
========================================
Repositorio documental para cotizaciones (MongoDB).
"""
from typing import List, Optional, Dict, Any
from database import MongoDB

class CotizacionesRepository:
    """
    Repositorio de Cotizaciones.
    Encapsula el acceso de lectura y escritura NoSQL de cotizaciones en MongoDB.
    """
    def __init__(self, db: MongoDB):
        self._db = db

    def get_all(self) -> List[Dict]:
        """
        Consulta todos los documentos de cotizaciones en MongoDB.
        """
        return self._db.get_all_cotizaciones()

    def get_by_codigo(self, codigo: str) -> Optional[Dict]:
        """
        Busca un documento específico por su código de cotización único.
        """
        return self._db.get_cotizacion(codigo)

    def get_ultimo_codigo(self, prefix: str) -> Optional[str]:
        """
        Obtiene el último código de cotización desde la base de datos documental.
        """
        return self._db.get_ultimo_codigo_cotizacion(prefix)

    def create(self, codigo: str, id_cliente: int, id_vehiculo: int,
               fecha_validez: Any, servicios: list, total: float) -> Dict:
        """
        Crea un nuevo documento de cotización embebido en MongoDB.
        """
        return self._db.create_cotizacion(
            codigo, id_cliente, id_vehiculo, fecha_validez, servicios, total
        )

