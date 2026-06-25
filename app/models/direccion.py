from sqlalchemy import String, Boolean, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Direccion(Base):
    __tablename__ = "direcciones"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id", ondelete="CASCADE"), index=True)
    alias: Mapped[str] = mapped_column(String(50))          # Ej: "Casa", "Oficina"
    direccion: Mapped[str] = mapped_column(String(255))
    ciudad: Mapped[str] = mapped_column(String(100))
    barrio: Mapped[str | None] = mapped_column(String(100), nullable=True)
    referencia: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    principal: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relaciones
    cliente: Mapped["Cliente"] = relationship(back_populates="direcciones")
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="direccion_entrega")
