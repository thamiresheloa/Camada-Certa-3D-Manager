from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base

if TYPE_CHECKING:
    from models.produto import Produto


class ItemVenda(Base):
    __tablename__ = "ItensVenda"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    venda_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("Vendas.id"), nullable=True)
    produto_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("Produtos.id"), nullable=True)
    quantidade: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    valor_unitario: Mapped[float | None] = mapped_column(Float, nullable=True)

    produto: Mapped["Produto"] = relationship(lazy="joined")
