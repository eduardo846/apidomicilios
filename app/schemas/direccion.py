from pydantic import BaseModel


class DireccionCreate(BaseModel):
    alias: str
    direccion: str
    ciudad: str
    barrio: str | None = None
    referencia: str | None = None
    latitud: float | None = None
    longitud: float | None = None
    principal: bool = False


class DireccionUpdate(BaseModel):
    alias: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    barrio: str | None = None
    referencia: str | None = None
    latitud: float | None = None
    longitud: float | None = None
    principal: bool | None = None


class DireccionOut(BaseModel):
    id: int
    cliente_id: int
    alias: str
    direccion: str
    ciudad: str
    barrio: str | None
    referencia: str | None
    latitud: float | None
    longitud: float | None
    principal: bool

    model_config = {"from_attributes": True}
