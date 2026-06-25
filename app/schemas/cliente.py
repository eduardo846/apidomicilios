from datetime import datetime
from pydantic import BaseModel, EmailStr


class ClienteCreate(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str
    password: str


class ClienteUpdate(BaseModel):
    nombre: str | None = None
    telefono: str | None = None


class ClienteOut(BaseModel):
    id: int
    nombre: str
    email: str
    telefono: str
    activo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}
