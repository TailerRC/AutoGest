"""
models/schemas/vehiculo.py
==========================
Contratos de datos para la entidad Vehículo (tabla Oracle: VEHICULOS).
"""
from pydantic import BaseModel, Field
from typing import Optional


class VehiculoCreate(BaseModel):
    id_cliente: int  = Field(..., description="FK → CLIENTES.id_cliente")
    placa:      str  = Field(..., min_length=6, max_length=10)
    marca:      str  = Field(..., min_length=1, max_length=50)
    modelo:     str  = Field(..., min_length=1, max_length=50)
    anio:       int  = Field(..., ge=1900, le=2100, description="Año del vehículo")


class VehiculoUpdate(BaseModel):
    id_cliente: Optional[int] = None
    placa:      Optional[str] = Field(None, min_length=6, max_length=10)
    marca:      Optional[str] = Field(None, min_length=1, max_length=50)
    modelo:     Optional[str] = Field(None, min_length=1, max_length=50)
    anio:       Optional[int] = Field(None, ge=1900, le=2100)


class VehiculoOut(BaseModel):
    id_vehiculo:     int
    id_cliente:      int
    placa:           str
    marca:           str
    modelo:          str
    año:             int
    nombre_cliente:  Optional[str] = None

    class Config:
        from_attributes = True
