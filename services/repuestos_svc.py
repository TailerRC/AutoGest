"""
services/repuestos_svc.py
==========================
Lógica de negocio para el inventario de Repuestos.
"""
from typing import List, Optional, Dict
from repositories.oracle.repuestos_repo import RepuestoRepository


class RepuestoService:
    """
    Servicio de Repuestos — reglas de negocio puras.
    INTEGRACIÓN: Gestiona los niveles de stock que luego disparan alertas globales y
    reabastecimiento desde Proveedores (MongoDB).
    """

    UMBRAL_CRITICO = 2
    UMBRAL_BAJO    = 5

    def __init__(self, repo: RepuestoRepository):
        self._repo = repo

    def listar(self) -> List[Dict]:
        """Retorna la lista de todos los repuestos."""
        return self._repo.get_all()

    def obtener(self, id_pieza: int) -> Optional[Dict]:
        """Retorna un repuesto específico por su ID."""
        return self._repo.get_by_id(id_pieza)

    def listar_criticos(self) -> List[Dict]:
        """
        Retorna repuestos con stock crítico.
        INTEGRACIÓN: Dispara alertas en el dashboard de AutoGest.
        """
        return self._repo.get_criticos(self.UMBRAL_CRITICO)

    def crear(self, codigo: str, nombre: str, stock: int,
              precio_venta: float, proveedor: str) -> Dict:
        """Valida y registra un nuevo repuesto en inventario."""
        if not codigo or not nombre:
            raise ValueError("Código y nombre son obligatorios.")
        if stock < 0:
            raise ValueError("El stock no puede ser negativo.")
        return self._repo.create(codigo.strip(), nombre.strip(),
                                  stock, precio_venta, proveedor.strip())

    def actualizar(self, id_pieza: int, codigo: str, nombre: str,
                   stock: int, precio_venta: float, proveedor: str) -> bool:
        """Valida y actualiza los detalles de un repuesto existente."""
        if not self._repo.get_by_id(id_pieza):
            return False
        return self._repo.update(id_pieza, codigo.strip(), nombre.strip(),
                                  stock, precio_venta, proveedor.strip())

    def eliminar(self, id_pieza: int) -> bool:
        """
        Elimina un repuesto del inventario de forma segura.
        INTEGRACIÓN: Si existen dependencias, aborta lanzando un ValueError para evitar la eliminación física.
        """
        if self._repo.tiene_dependencias(id_pieza):
            raise ValueError("No se puede eliminar el repuesto porque está asociado a órdenes de trabajo existentes.")
        return self._repo.delete(id_pieza)

