from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, func
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base


class Configuracao(Base):
    __tablename__ = "Configuracoes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    energia_kwh: Mapped[float | None] = mapped_column(Float, nullable=True)
    potencia_impressora: Mapped[float | None] = mapped_column(Float, nullable=True)
    percentual_desgaste: Mapped[float | None] = mapped_column(Float, nullable=True)
    lucro_padrao: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
