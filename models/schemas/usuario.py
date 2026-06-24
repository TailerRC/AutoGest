"""
models/schemas/usuario.py
=========================
Contratos de datos para Usuarios del sistema (tabla Oracle: USUARIOS).
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal

RolUsuario    = Literal["admin", "mecanico", "facturacion", "readonly"]
EstadoUsuario = Literal["activo", "inactivo"]


class UsuarioCreate(BaseModel):
    id_empleado: int          = Field(..., description="FK → EMPLEADOS.id_empleado")
    username:    str          = Field(..., min_length=3, max_length=30)
    password:    str          = Field(..., min_length=6)
    rol:         RolUsuario   = Field(...)


class UsuarioUpdate(BaseModel):
    id_empleado: Optional[int]          = None
    username:    Optional[str]          = Field(None, min_length=3, max_length=30)
    password:    Optional[str]          = Field(None, min_length=6)
    rol:         Optional[RolUsuario]   = None
    estado:      Optional[EstadoUsuario] = None


class UsuarioOut(BaseModel):
    id_usuario:     int
    id_empleado:    int
    username:       str
    rol:            str
    estado:         str
    nombre_empleado: Optional[str] = None

    class Config:
        from_attributes = True
