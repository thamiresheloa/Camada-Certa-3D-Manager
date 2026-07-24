from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base


class Filamento(Base):
    __tablename__ = "Filamentos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nome: Mapped[str | None] = mapped_column(String, nullable=True)
    marca: Mapped[str | None] = mapped_column(String, nullable=True)
    fornecedor: Mapped[str | None] = mapped_column(String, nullable=True)
    cor: Mapped[str | None] = mapped_column(String, nullable=True)
    tipo: Mapped[str | None] = mapped_column(String, nullable=True)
    valor_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    peso_original: Mapped[float | None] = mapped_column(Float, nullable=True)
    peso_restante: Mapped[float | None] = mapped_column(Float, nullable=True)
    data_compra: Mapped[date | None] = mapped_column(Date, nullable=True)
    validade: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
