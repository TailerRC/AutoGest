"""
services/proveedores_svc.py
===========================
Lógica de negocio para los Proveedores (MongoDB).
"""
import re
from typing import List, Optional, Dict
from repositories.mongo.proveedores_repo import ProveedoresRepository


class ProveedoresService:
    """
    Servicio de negocio para gestionar la lógica de proveedores.
    """
    def __init__(self, repo: ProveedoresRepository):
        self._repo = repo

    def listar(self) -> List[Dict]:
        """Retorna la lista de todos los proveedores."""
        return self._repo.get_all()

    def obtener_por_codigo(self, codigo: str) -> Optional[Dict]:
        """Retorna un proveedor dado su código."""
        return self._repo.get_by_codigo(codigo)

    def generar_siguiente_codigo(self, prefix: str = "PROV-") -> str:
        """
        Obtiene el último código de la base de datos e incrementa el correlativo.
        Ejemplo: Si el último es PROV-030, el siguiente será PROV-031.
        """
        ultimo_codigo = self._repo.get_ultimo_codigo(prefix)
        if not ultimo_codigo:
            return f"{prefix}001"
        try:
            # Extraer la parte numérica del final
            num_part = ultimo_codigo.split("-")[-1]
            siguiente_correlativo = int(num_part) + 1
            return f"{prefix}{siguiente_correlativo:03d}"
        except (ValueError, IndexError):
            # Fallback en caso de que no tenga formato estándar
            return f"{prefix}001"

    def validar_datos(self, nombre_empresa: str, lineas_productos: list, telefono: str, email: str):
        """
        Realiza las validaciones de negocio requeridas para un proveedor.
        """
        if not nombre_empresa or not nombre_empresa.strip():
            raise ValueError("La razón social es obligatoria.")

        if not telefono or not telefono.strip():
            raise ValueError("El teléfono es obligatorio.")
        
        # Validar que conste de exactamente 9 dígitos
        telefono_limpio = telefono.strip()
        if not re.match(r"^\d{9}$", telefono_limpio):
            raise ValueError("El teléfono debe tener exactamente 9 dígitos.")

        if not email or not email.strip():
            raise ValueError("El correo electrónico es obligatorio.")
            
        # Validar formato de email estándar
        email_limpio = email.strip()
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email_limpio):
            raise ValueError("El correo electrónico no es válido.")

        # Validar al menos una línea de producto no vacía
        lineas_validas = [l.strip() for l in lineas_productos if l.strip()]
        if not lineas_validas:
            raise ValueError("Debe ingresar al menos una línea de producto.")

    def crear(self, codigo: str, nombre_empresa: str, lineas_productos: list,
              telefono: str, email: str) -> Dict:
        """
        Valida y crea un nuevo proveedor. Genera el código automáticamente si es requerido o es 'AUTO'.
        """
        # Validar datos de entrada
        self.validar_datos(nombre_empresa, lineas_productos, telefono, email)

        # Generar código automático si no viene asignado o es 'AUTO'
        if not codigo or codigo.strip() == "" or codigo.strip().upper() == "AUTO":
            codigo = self.generar_siguiente_codigo()
        else:
            codigo = codigo.strip().upper()

        # Evitar duplicados
        existente = self.obtener_por_codigo(codigo)
        if existente:
            raise ValueError(f"Ya existe un proveedor registrado con el código {codigo}.")

        return self._repo.create(
            codigo,
            nombre_empresa.strip(),
            [l.strip() for l in lineas_productos if l.strip()],
            telefono.strip(),
            email.strip()
        )

    def actualizar(self, codigo: str, nombre_empresa: str, lineas_productos: list,
                   telefono: str, email: str) -> bool:
        """
        Valida y actualiza un proveedor existente.
        """
        self.validar_datos(nombre_empresa, lineas_productos, telefono, email)

        return self._repo.update(
            codigo.strip(),
            nombre_empresa.strip(),
            [l.strip() for l in lineas_productos if l.strip()],
            telefono.strip(),
            email.strip()
        )

