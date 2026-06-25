from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine, Base

# Importar todos los modelos para que Base los registre
from app.models import cliente, direccion, repartidor, pedido  # noqa: F401

from app.routers import auth, clientes, direcciones, repartidores, pedidos


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas al inicio (en producción usa Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="🛵 API de Domicilios",
    description="""
## API REST para gestión de domicilios / entregas a domicilio

### Funcionalidades:
- **Autenticación** con JWT (Bearer Token)
- **Clientes**: registro, perfil y gestión
- **Direcciones de entrega**: CRUD con soporte de coordenadas GPS
- **Repartidores**: gestión y estado en tiempo real
- **Pedidos**: ciclo de vida completo (PENDIENTE → EN_CAMINO → ENTREGADO)

### Flujo básico:
1. Registrarse en `POST /clientes/registro`
2. Obtener token en `POST /auth/login`
3. Usar el token como `Bearer` en el header `Authorization`
""",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(direcciones.router)
app.include_router(repartidores.router)
app.include_router(pedidos.router)


@app.get("/", tags=["Health"], summary="Health check")
async def root():
    return {"status": "ok", "service": "API de Domicilios", "version": "1.0.0"}
