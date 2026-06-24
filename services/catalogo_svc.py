"""
services/catalogo_svc.py
=========================
Lógica de negocio para el Catálogo Técnico (MongoDB).
"""
from typing import List, Optional, Dict
from repositories.mongo.catalogo_repo import CatalogoRepository


class CatalogoService:
    """
    Servicio del Catálogo Técnico — reglas de negocio puras.
    """

    def __init__(self, repo: CatalogoRepository):
        self._repo = repo

    def listar(self) -> List[Dict]:
        return self._repo.get_all()

    def buscar(self, marca: str = "", modelo: str = "",
               año: Optional[int] = None) -> List[Dict]:
        """Búsqueda flexible por marca, modelo y/o año."""
        return self._repo.buscar(marca=marca.strip(), modelo=modelo.strip(), año=año)

    def buscar_por_vehiculo(self, vehiculo: Dict) -> Optional[Dict]:
        """
        Busca la ficha técnica que coincide con un vehículo concreto.
        Retorna la primera coincidencia o None.
        """
        resultados = self._repo.buscar(
            marca=vehiculo.get("marca", ""),
            modelo=vehiculo.get("modelo", ""),
            año=vehiculo.get("año"),
        )
        return resultados[0] if resultados else None
