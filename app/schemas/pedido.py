from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.models.pedido import EstadoPedido


class PedidoCreate(BaseModel):
    direccion_entrega_id: int
    descripcion: str
    total: Decimal
    notas: str | None = None


class PedidoUpdate(BaseModel):
    estado: EstadoPedido | None = None
    repartidor_id: int | None = None
    notas: str | None = None


class PedidoOut(BaseModel):
    id: int
    cliente_id: int
    repartidor_id: int | None
    direccion_entrega_id: int
    estado: EstadoPedido
    descripcion: str
    total: Decimal
    notas: str | None
    creado_en: datetime
    actualizado_en: datetime
    entregado_en: datetime | None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
