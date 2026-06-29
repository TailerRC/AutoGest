"""
services/cotizaciones_svc.py
============================
Lógica de negocio para las Cotizaciones (MongoDB).
"""
import uuid
from typing import List, Optional, Dict
from datetime import datetime
from repositories.mongo.cotizaciones_repo import CotizacionesRepository


class CotizacionesService:
    """
    Servicio de Cotizaciones — contiene reglas y validaciones de negocio puras.
    No depende del framework FastHTML ni de peticiones HTTP directamente.
    """
    def __init__(self, repo: CotizacionesRepository):
        self._repo = repo

    def listar(self) -> List[Dict]:
        """
        Retorna la lista completa de cotizaciones desde el repositorio.
        """
        return self._repo.get_all()

    def obtener_por_codigo(self, codigo: str) -> Optional[Dict]:
        """
        Busca y retorna una cotización por su código único.
        """
        return self._repo.get_by_codigo(codigo)

    def crear(self, id_cliente: int, id_vehiculo: int,
              fecha_validez: str, servicios: list, total: float) -> Dict:
        """
        Crea y registra una nueva cotización.
        
        Reglas y Validaciones de negocio:
          - El cliente y vehículo deben ser seleccionados.
          - La fecha de validez es requerida.
          - Debe existir al menos un ítem cotizado.
          - Sanitiza los ítems mapeándolos con la clave 'item' oficial.
          - Recalcula el total del lado del servidor para evitar alteraciones maliciosas.
          - Convierte la fecha de validez a tipo datetime para consistencia en MongoDB.
        """
        if not id_cliente:
            raise ValueError("El cliente es obligatorio.")
        if not id_vehiculo:
            raise ValueError("El vehículo es obligatorio.")
        if not fecha_validez:
            raise ValueError("La fecha de validez es obligatoria.")
        if not servicios or len(servicios) == 0:
            raise ValueError("Debe agregar al menos un servicio o repuesto a la cotización.")
            
        calculated_total = 0.0
        cleaned_servicios = []
        
        # Validar y sanitizar cada ítem de servicio/repuesto
        for s in servicios:
            # Obtener descripción soportando fallbacks por inconsistencias antiguas
            item_name = s.get("item", "").strip()
            if not item_name:
                item_name = s.get("descripcion", "").strip()
            
            if not item_name:
                raise ValueError("Cada ítem agregado debe tener una descripción válida.")
                
            try:
                precio = float(s.get("precio", 0.0))
            except (TypeError, ValueError):
                raise ValueError(f"El precio del ítem '{item_name}' debe ser un valor numérico.")
                
            if precio < 0:
                raise ValueError(f"El precio del ítem '{item_name}' no puede ser negativo.")
                
            calculated_total += precio
            cleaned_servicios.append({
                "item": item_name,
                "precio": precio
            })
            
        # Generar código correlativo incremental (COT-YYYY-NNN) para continuidad numérica NoSQL
        year = datetime.now().year
        prefix = f"COT-{year}-"
        
        ultimo_codigo = self._repo.get_ultimo_codigo(prefix)
        if ultimo_codigo:
            try:
                # Extrae el correlativo del último código de cotización e incrementa el valor
                partes = ultimo_codigo.split("-")
                correlativo = int(partes[-1]) + 1
            except (ValueError, IndexError):
                correlativo = 1
        else:
            correlativo = 1
            
        codigo = f"{prefix}{correlativo:03d}"
        
        # Intentar parsear fecha a datetime.datetime para almacenamiento NoSQL estándar
        try:
            fecha_dt = datetime.strptime(fecha_validez, "%Y-%m-%d")
        except Exception:
            fecha_dt = fecha_validez
            
        return self._repo.create(codigo, int(id_cliente), int(id_vehiculo),
                                 fecha_dt, cleaned_servicios, calculated_total)
    
    def listar_vigentes_por_vehiculo(self, id_vehiculo: int) -> List[Dict]:
        """
        Retorna las cotizaciones de un vehículo cuya fecha_validez aún no venció,
        ordenadas de la más reciente a la más antigua (por código de cotización).
        La más reciente (primera de la lista) es la que se considera "la actual"
        para efectos de carga en una orden.
        """
        hoy = datetime.now()
        todas = self._repo.get_all()
        resultado = []
        for c in todas:
            if c.get("idVehiculo") != id_vehiculo:
                continue
            fecha_val = c.get("fecha_validez")
            if hasattr(fecha_val, "date"):
                vence = fecha_val
            else:
                try:
                    vence = datetime.strptime(str(fecha_val)[:10], "%Y-%m-%d")
                except Exception:
                    continue
            if vence >= hoy:
                resultado.append(c)

        resultado.sort(key=lambda c: c.get("codigoCotizacion", ""), reverse=True)
        return resultado