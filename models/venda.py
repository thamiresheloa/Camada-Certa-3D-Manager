from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base

if TYPE_CHECKING:
    from models.item_venda import ItemVenda


class Venda(Base):
    __tablename__ = "Vendas"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cliente: Mapped[str | None] = mapped_column(String, nullable=True)
    canal: Mapped[str | None] = mapped_column(String, nullable=True)
    valor_venda: Mapped[float | None] = mapped_column(Float, nullable=True)
    forma_pagamento: Mapped[str | None] = mapped_column(String, nullable=True)
    pago: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    data_venda: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    itens: Mapped[list["ItemVenda"]] = relationship(lazy="selectin", cascade="all, delete-orphan")
