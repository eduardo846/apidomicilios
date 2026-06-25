from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteOut
from app.core.security import hash_password, get_current_user

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("/registro", response_model=ClienteOut, status_code=status.HTTP_201_CREATED, summary="Registrar cliente")
async def registrar_cliente(data: ClienteCreate, db: AsyncSession = Depends(get_db)):
    """Crea un nuevo cliente. No requiere autenticación."""
    existe = await db.execute(select(Cliente).where(Cliente.email == data.email))
    if existe.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    cliente = Cliente(
        nombre=data.nombre,
        email=data.email,
        telefono=data.telefono,
        hashed_password=hash_password(data.password),
    )
    db.add(cliente)
    await db.flush()
    await db.refresh(cliente)
    return cliente


@router.get("/me", response_model=ClienteOut, summary="Mi perfil")
async def mi_perfil(current: Cliente = Depends(get_current_user)):
    """Devuelve el perfil del cliente autenticado."""
    return current


@router.put("/me", response_model=ClienteOut, summary="Actualizar mi perfil")
async def actualizar_perfil(
    data: ClienteUpdate,
    db: AsyncSession = Depends(get_db),
    current: Cliente = Depends(get_current_user),
):
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(current, field, value)
    await db.flush()
    await db.refresh(current)
    return current


@router.get("/", response_model=list[ClienteOut], summary="Listar clientes")
async def listar_clientes(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: Cliente = Depends(get_current_user),
):
    """Lista todos los clientes (requiere autenticación)."""
    result = await db.execute(select(Cliente).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{cliente_id}", response_model=ClienteOut, summary="Obtener cliente por ID")
async def obtener_cliente(
    cliente_id: int,
    db: AsyncSession = Depends(get_db),
    _: Cliente = Depends(get_current_user),
):
    result = await db.execute(select(Cliente).where(Cliente.id == cliente_id))
    cliente = result.scalar_one_or_none()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar cliente")
async def desactivar_cliente(
    cliente_id: int,
    db: AsyncSession = Depends(get_db),
    _: Cliente = Depends(get_current_user),
):
    result = await db.execute(select(Cliente).where(Cliente.id == cliente_id))
    cliente = result.scalar_one_or_none()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente.activo = False
    await db.flush()
