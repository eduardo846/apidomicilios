from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.cliente import Cliente
from app.schemas.pedido import Token
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token, summary="Login de cliente")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Autentica un cliente y devuelve un token JWT.

    - **username**: email del cliente
    - **password**: contraseña
    """
    result = await db.execute(select(Cliente).where(Cliente.email == form_data.username))
    cliente = result.scalar_one_or_none()

    if not cliente or not verify_password(form_data.password, cliente.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not cliente.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cuenta inactiva")

    token = create_access_token(data={"sub": str(cliente.id)})
    return {"access_token": token, "token_type": "bearer"}
