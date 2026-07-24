from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base

if TYPE_CHECKING:
    from models.produto import Produto


class Venda(Base):
    __tablename__ = "Vendas"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    produto_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("Produtos.id"), nullable=True)
    quantidade: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    cliente: Mapped[str | None] = mapped_column(String, nullable=True)
    canal: Mapped[str | None] = mapped_column(String, nullable=True)
    valor_venda: Mapped[float | None] = mapped_column(Float, nullable=True)
    forma_pagamento: Mapped[str | None] = mapped_column(String, nullable=True)
    data_venda: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    produto: Mapped["Produto"] = relationship(lazy="joined")
