from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.repartidor import EstadoRepartidor


class RepartidorCreate(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str
    password: str
    vehiculo: str | None = None
    placa: str | None = None


class RepartidorUpdate(BaseModel):
    nombre: str | None = None
    telefono: str | None = None
    vehiculo: str | None = None
    placa: str | None = None
    estado: EstadoRepartidor | None = None


class RepartidorOut(BaseModel):
    id: int
    nombre: str
    email: str
    telefono: str
    vehiculo: str | None
    placa: str | None
    estado: EstadoRepartidor
    activo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}
