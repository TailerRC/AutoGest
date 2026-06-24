"""
models/schemas/orden.py
=======================
Contratos de datos para Órdenes de Trabajo (tabla Oracle: ORDENES_TRABAJO).
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal

EstadoOrden = Literal["pendiente", "en_proceso", "completada", "cancelada"]


class OrdenCreate(BaseModel):
    id_vehiculo:   int = Field(..., description="FK → VEHICULOS.id_vehiculo")
    id_empleado:   int = Field(..., description="FK → EMPLEADOS.id_empleado")
    fecha_ingreso: str = Field(..., description="Fecha de ingreso YYYY-MM-DD")
    fecha_entrega: str = Field(..., description="Fecha estimada de entrega YYYY-MM-DD")


class OrdenUpdate(BaseModel):
    id_vehiculo:   Optional[int]        = None
    id_empleado:   Optional[int]        = None
    fecha_ingreso: Optional[str]        = None
    fecha_entrega: Optional[str]        = None
    estado:        Optional[EstadoOrden] = None


class OrdenOut(BaseModel):
    id_orden:       int
    id_vehiculo:    int
    id_empleado:    int
    fecha_ingreso:  str
    fecha_entrega:  str
    estado:         str
    placa:          Optional[str] = None
    nombre_cliente: Optional[str] = None
    nombre_empleado: Optional[str] = None

    class Config:
        from_attributes = True
