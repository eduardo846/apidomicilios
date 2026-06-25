from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.cliente import Cliente
from app.models.repartidor import Repartidor, EstadoRepartidor
from app.schemas.repartidor import RepartidorCreate, RepartidorUpdate, RepartidorOut
from app.core.security import hash_password, get_current_user

router = APIRouter(prefix="/repartidores", tags=["Repartidores"])


@router.post("/", response_model=RepartidorOut, status_code=status.HTTP_201_CREATED, summary="Registrar repartidor")
async def registrar_repartidor(
    data: RepartidorCreate,
    db: AsyncSession = Depends(get_db),
    _: Cliente = Depends(get_current_user),
):
    existe = await db.execute(select(Repartidor).where(Repartidor.email == data.email))
    if existe.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email ya registrado")

    repartidor = Repartidor(
        nombre=data.nombre,
        email=data.email,
        telefono=data.telefono,
        hashed_password=hash_password(data.password),
        vehiculo=data.vehiculo,
        placa=data.placa,
    )
    db.add(repartidor)
    await db.flush()
    await db.refresh(repartidor)
    return repartidor


@router.get("/", response_model=list[RepartidorOut], summary="Listar repartidores")
async def listar_repartidores(
    estado: EstadoRepartidor | None = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: Cliente = Depends(get_current_user),
):
    """Lista repartidores, opcionalmente filtrando por estado."""
    query = select(Repartidor).where(Repartidor.activo == True)
    if estado:
        query = query.where(Repartidor.estado == estado)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{repartidor_id}", response_model=RepartidorOut, summary="Obtener repartidor")
async def obtener_repartidor(
    repartidor_id: int,
    db: AsyncSession = Depends(get_db),
    _: Cliente = Depends(get_current_user),
):
    result = await db.execute(select(Repartidor).where(Repartidor.id == repartidor_id))
    repartidor = result.scalar_one_or_none()
    if not repartidor:
        raise HTTPException(status_code=404, detail="Repartidor no encontrado")
    return repartidor


@router.put("/{repartidor_id}", response_model=RepartidorOut, summary="Actualizar repartidor")
async def actualizar_repartidor(
    repartidor_id: int,
    data: RepartidorUpdate,
    db: AsyncSession = Depends(get_db),
    _: Cliente = Depends(get_current_user),
):
    result = await db.execute(select(Repartidor).where(Repartidor.id == repartidor_id))
    repartidor = result.scalar_one_or_none()
    if not repartidor:
        raise HTTPException(status_code=404, detail="Repartidor no encontrado")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(repartidor, field, value)

    await db.flush()
    await db.refresh(repartidor)
    return repartidor


@router.delete("/{repartidor_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar repartidor")
async def desactivar_repartidor(
    repartidor_id: int,
    db: AsyncSession = Depends(get_db),
    _: Cliente = Depends(get_current_user),
):
    result = await db.execute(select(Repartidor).where(Repartidor.id == repartidor_id))
    repartidor = result.scalar_one_or_none()
    if not repartidor:
        raise HTTPException(status_code=404, detail="Repartidor no encontrado")
    repartidor.activo = False
    await db.flush()
