from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.session import Base


class EstadoRepartidor(str, enum.Enum):
    DISPONIBLE = "DISPONIBLE"
    OCUPADO = "OCUPADO"
    INACTIVO = "INACTIVO"


class Repartidor(Base):
    __tablename__ = "repartidores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    telefono: Mapped[str] = mapped_column(String(20))
    hashed_password: Mapped[str] = mapped_column(String(255))
    vehiculo: Mapped[str | None] = mapped_column(String(50), nullable=True)  # Ej: "Moto", "Bicicleta"
    placa: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estado: Mapped[EstadoRepartidor] = mapped_column(
        SAEnum(EstadoRepartidor), default=EstadoRepartidor.DISPONIBLE
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="repartidor")
