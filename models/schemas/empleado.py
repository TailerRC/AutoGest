"""
models/schemas/empleado.py
==========================
Contratos de datos para la entidad Empleado (tabla Oracle: EMPLEADOS).
"""
from pydantic import BaseModel, Field
from typing import Optional


class EmpleadoCreate(BaseModel):
    nombre:       str = Field(..., min_length=2, max_length=100)
    cargo:        str = Field(..., min_length=2, max_length=60)
    especialidad: str = Field(..., min_length=2, max_length=80)


class EmpleadoUpdate(BaseModel):
    nombre:       Optional[str] = Field(None, min_length=2, max_length=100)
    cargo:        Optional[str] = Field(None, min_length=2, max_length=60)
    especialidad: Optional[str] = Field(None, min_length=2, max_length=80)


class EmpleadoOut(BaseModel):
    id_empleado:  int
    nombre:       str
    cargo:        str
    especialidad: str

    class Config:
        from_attributes = True
