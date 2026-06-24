"""
models/schemas/factura.py
=========================
Contratos de datos para Facturas (tabla Oracle: FACTURAS).
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal

EstadoPago    = Literal["pendiente", "pagada"]
MetodoPago    = Literal["Efectivo", "Tarjeta Débito", "Tarjeta Crédito", "Transferencia"]


class FacturaCreate(BaseModel):
    id_orden:    int       = Field(..., description="FK → ORDENES_TRABAJO.id_orden")
    total:       float     = Field(..., ge=0)
    metodo_pago: MetodoPago = Field(...)


class FacturaOut(BaseModel):
    id_factura:     int
    id_orden:       int
    fecha:          str
    total:          float
    metodo_pago:    str
    estado_pago:    str
    nombre_cliente: Optional[str] = None
    placa:          Optional[str] = None

    class Config:
        from_attributes = True
