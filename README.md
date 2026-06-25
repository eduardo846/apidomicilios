# 🛵 API de Domicilios — FastAPI + PostgreSQL + JWT

API REST completa para gestión de domicilios/entregas a domicilio.

---

## Estructura del proyecto

```
domicilios-api/
├── app/
│   ├── main.py                  # Entrada principal
│   ├── core/
│   │   ├── config.py            # Variables de entorno
│   │   └── security.py          # JWT + hashing
│   ├── db/
│   │   └── session.py           # Motor async y Base declarativa
│   ├── models/
│   │   ├── cliente.py
│   │   ├── direccion.py
│   │   ├── repartidor.py
│   │   └── pedido.py
│   ├── schemas/
│   │   ├── cliente.py
│   │   ├── direccion.py
│   │   ├── repartidor.py
│   │   └── pedido.py
│   └── routers/
│       ├── auth.py
│       ├── clientes.py
│       ├── direcciones.py
│       ├── repartidores.py
│       └── pedidos.py
├── requirements.txt
└── .env.example
```

---

## Instalación y arranque

### 1. Clonar y crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales de PostgreSQL y clave JWT
```

### 3. Crear la base de datos en PostgreSQL
```sql
CREATE DATABASE domicilios_db;
```

### 4. Levantar la API
```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Documentación interactiva
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Flujo de uso rápido

```bash
# 1. Registrar cliente
curl -X POST http://localhost:8000/clientes/registro \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Juan","email":"juan@mail.com","telefono":"3001234567","password":"secreto123"}'

# 2. Login → obtener token
curl -X POST http://localhost:8000/auth/login \
  -d "username=juan@mail.com&password=secreto123"

# 3. Usar token en siguientes llamadas
TOKEN="eyJ..."
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/clientes/me
```

---

## Endpoints

| Método | Ruta                         | Descripción                      | Auth |
|--------|------------------------------|----------------------------------|------|
| POST   | `/clientes/registro`         | Registrar cliente                | ❌   |
| POST   | `/auth/login`                | Login → token JWT                | ❌   |
| GET    | `/clientes/me`               | Mi perfil                        | ✅   |
| PUT    | `/clientes/me`               | Actualizar perfil                | ✅   |
| GET    | `/clientes/`                 | Listar clientes                  | ✅   |
| POST   | `/direcciones/`              | Agregar dirección de entrega     | ✅   |
| GET    | `/direcciones/`              | Mis direcciones                  | ✅   |
| PUT    | `/direcciones/{id}`          | Actualizar dirección             | ✅   |
| DELETE | `/direcciones/{id}`          | Eliminar dirección               | ✅   |
| POST   | `/repartidores/`             | Registrar repartidor             | ✅   |
| GET    | `/repartidores/`             | Listar repartidores (filtro)     | ✅   |
| PUT    | `/repartidores/{id}`         | Actualizar estado/datos          | ✅   |
| POST   | `/pedidos/`                  | Crear pedido                     | ✅   |
| GET    | `/pedidos/`                  | Mis pedidos                      | ✅   |
| GET    | `/pedidos/todos`             | Todos los pedidos (admin)        | ✅   |
| PATCH  | `/pedidos/{id}`              | Actualizar estado/repartidor     | ✅   |
| DELETE | `/pedidos/{id}`              | Cancelar pedido                  | ✅   |

---

## Estados del Pedido

```
PENDIENTE → CONFIRMADO → EN_CAMINO → ENTREGADO
                ↓
           CANCELADO
```

## Estados del Repartidor

- `DISPONIBLE` — Listo para asignación
- `OCUPADO` — Con entrega activa
- `INACTIVO` — Fuera de servicio

---

## Variables de entorno (.env)

| Variable                      | Descripción                       |
|-------------------------------|-----------------------------------|
| `DATABASE_URL`                | URL async de PostgreSQL           |
| `SECRET_KEY`                  | Clave secreta para firmar JWT     |
| `ALGORITHM`                   | Algoritmo JWT (default: HS256)    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración del token (default: 60)|
