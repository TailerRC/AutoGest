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
        """Obtiene la lista completa del catálogo."""
        return self._repo.get_all()

    def buscar(self, marca: str = "", modelo: str = "",
               año: Optional[int] = None, codigo: str = "",
               motor: str = "", aceite: str = "") -> List[Dict]:
        """
        Búsqueda avanzada por marca, modelo, año, código de especificación, motor y aceite.
        Realiza el filtrado en memoria para asegurar compatibilidad y velocidad.
        """
        todos = self._repo.get_all()
        filtrados = []
        for esp in todos:
            det_tec = esp.get("detalles_tecnicos", {})
            
            # Filtro por código de especificación
            if codigo and codigo.strip():
                if codigo.strip().lower() not in esp.get("codigoEspecificacion", "").lower():
                    continue
            
            # Filtro por marca
            if marca and marca.strip():
                if marca.strip().lower() not in esp.get("marca", "").lower():
                    continue
                    
            # Filtro por modelo
            if modelo and modelo.strip():
                if modelo.strip().lower() not in esp.get("modelo", "").lower():
                    continue
                    
            # Filtro por año
            if año is not None:
                try:
                    if int(esp.get("anio", 0)) != int(año):
                        continue
                except (ValueError, TypeError):
                    continue
                    
            # Filtro por motor
            if motor and motor.strip():
                if motor.strip().lower() not in det_tec.get("motor", "").lower():
                    continue
                    
            # Filtro por aceite recomendado
            if aceite and aceite.strip():
                if aceite.strip().lower() not in det_tec.get("aceite", "").lower():
                    continue
                    
            filtrados.append(esp)
        return filtrados

    def buscar_por_vehiculo(self, vehiculo: Dict) -> Optional[Dict]:
        """
        Busca la ficha técnica que coincide con un vehículo concreto.
        Retorna la primera coincidencia o None.
        """
        resultados = self.buscar(
            marca=vehiculo.get("marca", ""),
            modelo=vehiculo.get("modelo", ""),
            año=vehiculo.get("año"),
        )
        return resultados[0] if resultados else None

    def actualizar(self, codigo: str, marca: str, modelo: str, anio: int,
                motor: str, aceite: str, transmision: str = "",
                bujias: str = "", bateria: str = "", otros: str = "") -> bool:
        """
        Reglas de negocio:
        - El código de especificación debe existir.
        - Marca, modelo y año son obligatorios.
        """
        if not marca or not marca.strip():
            raise ValueError("La marca es obligatoria.")
        if not modelo or not modelo.strip():
            raise ValueError("El modelo es obligatorio.")
        existe = any(e.get("codigoEspecificacion") == codigo for e in self._repo.get_all())
        if not existe:
            raise ValueError(f"La especificación '{codigo}' no existe.")
        return self._repo.actualizar(
            codigo, marca.strip(), modelo.strip(), anio,
            motor.strip(), aceite.strip(), transmision.strip(),
            bujias.strip(), bateria.strip(), otros.strip()
        )