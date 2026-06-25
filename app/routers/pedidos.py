from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.cliente import Cliente
from app.models.pedido import Pedido, EstadoPedido
from app.models.direccion import Direccion
from app.schemas.pedido import PedidoCreate, PedidoUpdate, PedidoOut
from app.core.security import get_current_user

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("/", response_model=PedidoOut, status_code=status.HTTP_201_CREATED, summary="Crear pedido")
async def crear_pedido(
    data: PedidoCreate,
    db: AsyncSession = Depends(get_db),
    current: Cliente = Depends(get_current_user),
):
    """Crea un nuevo pedido asociado al cliente autenticado."""
    # Verificar que la dirección pertenece al cliente
    dir_result = await db.execute(
        select(Direccion).where(
            Direccion.id == data.direccion_entrega_id,
            Direccion.cliente_id == current.id,
        )
    )
    if not dir_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Dirección de entrega no válida")

    pedido = Pedido(**data.model_dump(), cliente_id=current.id)
    db.add(pedido)
    await db.flush()
    await db.refresh(pedido)
    return pedido


@router.get("/", response_model=list[PedidoOut], summary="Mis pedidos")
async def mis_pedidos(
    estado: EstadoPedido | None = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current: Cliente = Depends(get_current_user),
):
    """Lista los pedidos del cliente autenticado, con filtro opcional por estado."""
    query = select(Pedido).where(Pedido.cliente_id == current.id)
    if estado:
        query = query.where(Pedido.estado == estado)
    result = await db.execute(query.order_by(Pedido.creado_en.desc()).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/todos", response_model=list[PedidoOut], summary="Todos los pedidos (admin)")
async def todos_los_pedidos(
    estado: EstadoPedido | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: Cliente = Depends(get_current_user),
):
    """Lista todos los pedidos del sistema."""
    query = select(Pedido)
    if estado:
        query = query.where(Pedido.estado == estado)
    result = await db.execute(query.order_by(Pedido.creado_en.desc()).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{pedido_id}", response_model=PedidoOut, summary="Obtener pedido")
async def obtener_pedido(
    pedido_id: int,
    db: AsyncSession = Depends(get_db),
    current: Cliente = Depends(get_current_user),
):
    result = await db.execute(select(Pedido).where(Pedido.id == pedido_id))
    pedido = result.scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido


@router.patch("/{pedido_id}", response_model=PedidoOut, summary="Actualizar pedido")
async def actualizar_pedido(
    pedido_id: int,
    data: PedidoUpdate,
    db: AsyncSession = Depends(get_db),
    _: Cliente = Depends(get_current_user),
):
    """
    Actualiza estado, repartidor asignado o notas de un pedido.
    Cuando el estado pasa a ENTREGADO, registra la fecha/hora.
    """
    result = await db.execute(select(Pedido).where(Pedido.id == pedido_id))
    pedido = result.scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    updates = data.model_dump(exclude_none=True)

    if "estado" in updates and updates["estado"] == EstadoPedido.ENTREGADO:
        pedido.entregado_en = datetime.now(timezone.utc)

    for field, value in updates.items():
        setattr(pedido, field, value)

    await db.flush()
    await db.refresh(pedido)
    return pedido


@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Cancelar pedido")
async def cancelar_pedido(
    pedido_id: int,
    db: AsyncSession = Depends(get_db),
    current: Cliente = Depends(get_current_user),
):
    result = await db.execute(
        select(Pedido).where(Pedido.id == pedido_id, Pedido.cliente_id == current.id)
    )
    pedido = result.scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if pedido.estado not in (EstadoPedido.PENDIENTE, EstadoPedido.CONFIRMADO):
        raise HTTPException(status_code=400, detail="No se puede cancelar un pedido en curso o entregado")

    pedido.estado = EstadoPedido.CANCELADO
    await db.flush()
