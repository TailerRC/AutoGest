"""
models/schemas/cliente.py
=========================
Contratos de datos para la entidad Cliente (tabla Oracle: CLIENTES).
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class ClienteCreate(BaseModel):
    """Datos requeridos para crear un nuevo cliente."""
    nombre:   str = Field(..., min_length=2, max_length=100, description="Nombre completo del cliente")
    dni:      str = Field(..., min_length=8, max_length=8,   description="DNI de 8 dígitos")
    telefono: str = Field(..., min_length=7, max_length=20,  description="Número de teléfono")
    email:    str = Field(..., max_length=100,               description="Correo electrónico")


class ClienteUpdate(BaseModel):
    """Datos para actualizar un cliente existente."""
    nombre:   Optional[str] = Field(None, min_length=2, max_length=100)
    dni:      Optional[str] = Field(None, min_length=8, max_length=8)
    telefono: Optional[str] = Field(None, min_length=7, max_length=20)
    email:    Optional[str] = Field(None, max_length=100)


class ClienteOut(BaseModel):
    """Representación de un cliente al salir de la base de datos."""
    id_cliente: int
    nombre:     str
    dni:        str
    telefono:   str
    email:      str

    class Config:
        from_attributes = True
