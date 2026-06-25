from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.cliente import Cliente
from app.models.direccion import Direccion
from app.schemas.direccion import DireccionCreate, DireccionUpdate, DireccionOut
from app.core.security import get_current_user

router = APIRouter(prefix="/direcciones", tags=["Direcciones de entrega"])


@router.post("/", response_model=DireccionOut, status_code=status.HTTP_201_CREATED, summary="Agregar dirección")
async def agregar_direccion(
    data: DireccionCreate,
    db: AsyncSession = Depends(get_db),
    current: Cliente = Depends(get_current_user),
):
    """Agrega una dirección de entrega al cliente autenticado."""
    # Si se marca como principal, desmarcar las existentes
    if data.principal:
        result = await db.execute(
            select(Direccion).where(Direccion.cliente_id == current.id, Direccion.principal == True)
        )
        for d in result.scalars().all():
            d.principal = False

    direccion = Direccion(**data.model_dump(), cliente_id=current.id)
    db.add(direccion)
    await db.flush()
    await db.refresh(direccion)
    return direccion


@router.get("/", response_model=list[DireccionOut], summary="Mis direcciones")
async def mis_direcciones(
    db: AsyncSession = Depends(get_db),
    current: Cliente = Depends(get_current_user),
):
    result = await db.execute(select(Direccion).where(Direccion.cliente_id == current.id))
    return result.scalars().all()


@router.get("/{direccion_id}", response_model=DireccionOut, summary="Obtener dirección")
async def obtener_direccion(
    direccion_id: int,
    db: AsyncSession = Depends(get_db),
    current: Cliente = Depends(get_current_user),
):
    result = await db.execute(
        select(Direccion).where(Direccion.id == direccion_id, Direccion.cliente_id == current.id)
    )
    direccion = result.scalar_one_or_none()
    if not direccion:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    return direccion


@router.put("/{direccion_id}", response_model=DireccionOut, summary="Actualizar dirección")
async def actualizar_direccion(
    direccion_id: int,
    data: DireccionUpdate,
    db: AsyncSession = Depends(get_db),
    current: Cliente = Depends(get_current_user),
):
    result = await db.execute(
        select(Direccion).where(Direccion.id == direccion_id, Direccion.cliente_id == current.id)
    )
    direccion = result.scalar_one_or_none()
    if not direccion:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")

    if data.principal:
        otras = await db.execute(
            select(Direccion).where(Direccion.cliente_id == current.id, Direccion.principal == True)
        )
        for d in otras.scalars().all():
            d.principal = False

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(direccion, field, value)

    await db.flush()
    await db.refresh(direccion)
    return direccion


@router.delete("/{direccion_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar dirección")
async def eliminar_direccion(
    direccion_id: int,
    db: AsyncSession = Depends(get_db),
    current: Cliente = Depends(get_current_user),
):
    result = await db.execute(
        select(Direccion).where(Direccion.id == direccion_id, Direccion.cliente_id == current.id)
    )
    direccion = result.scalar_one_or_none()
    if not direccion:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    await db.delete(direccion)
    await db.flush()
