from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, ForeignKey, Numeric, Text, func, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.session import Base


class EstadoPedido(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    EN_CAMINO = "EN_CAMINO"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), index=True)
    repartidor_id: Mapped[int | None] = mapped_column(ForeignKey("repartidores.id"), nullable=True, index=True)
    direccion_entrega_id: Mapped[int] = mapped_column(ForeignKey("direcciones.id"), index=True)

    estado: Mapped[EstadoPedido] = mapped_column(
        SAEnum(EstadoPedido), default=EstadoPedido.PENDIENTE, index=True
    )
    descripcion: Mapped[str] = mapped_column(Text)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)

    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    entregado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relaciones
    cliente: Mapped["Cliente"] = relationship(back_populates="pedidos")
    repartidor: Mapped["Repartidor | None"] = relationship(back_populates="pedidos")
    direccion_entrega: Mapped["Direccion"] = relationship(back_populates="pedidos")
