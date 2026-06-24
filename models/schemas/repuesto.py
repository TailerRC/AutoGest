"""
models/schemas/repuesto.py
==========================
Contratos de datos para Repuestos/Inventario (tabla Oracle: INVENTARIO_REPUESTOS).
"""
from pydantic import BaseModel, Field
from typing import Optional


class RepuestoCreate(BaseModel):
    codigo:       str   = Field(..., min_length=3, max_length=20)
    nombre:       str   = Field(..., min_length=2, max_length=100)
    stock:        int   = Field(..., ge=0)
    precio_venta: float = Field(..., ge=0)
    proveedor:    str   = Field(..., min_length=2, max_length=80)


class RepuestoUpdate(BaseModel):
    codigo:       Optional[str]   = Field(None, min_length=3, max_length=20)
    nombre:       Optional[str]   = Field(None, min_length=2, max_length=100)
    stock:        Optional[int]   = Field(None, ge=0)
    precio_venta: Optional[float] = Field(None, ge=0)
    proveedor:    Optional[str]   = Field(None, min_length=2, max_length=80)


class RepuestoOut(BaseModel):
    id_pieza:     int
    codigo:       str
    nombre:       str
    stock:        int
    precio_venta: float
    proveedor:    str

    class Config:
        from_attributes = True
