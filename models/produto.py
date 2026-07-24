from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base

if TYPE_CHECKING:
    from models.filamento import Filamento


class Produto(Base):
    __tablename__ = "Produtos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nome: Mapped[str | None] = mapped_column(String, nullable=True)
    filamento_id: Mapped[int | None] = mapped_column(SmallInteger, ForeignKey("Filamentos.id"), nullable=True)
    peso: Mapped[float | None] = mapped_column(Float, nullable=True)
    tempo: Mapped[float | None] = mapped_column(Float, nullable=True)
    custo_filamento: Mapped[float | None] = mapped_column(Float, nullable=True)
    custo_energia: Mapped[float | None] = mapped_column(Float, nullable=True)
    custo_desgaste: Mapped[float | None] = mapped_column(Float, nullable=True)
    custo_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    preco_sugerido: Mapped[float | None] = mapped_column(Float, nullable=True)
    lucro: Mapped[float | None] = mapped_column(Float, nullable=True)
    observacao: Mapped[str | None] = mapped_column(String, nullable=True)
    foto: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    filamento: Mapped["Filamento"] = relationship(lazy="joined")
