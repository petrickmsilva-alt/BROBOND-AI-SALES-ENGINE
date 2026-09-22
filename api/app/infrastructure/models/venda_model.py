"""ORM mapping for vendas."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.types import GUID

if TYPE_CHECKING:
    from app.infrastructure.models.cliente_model import ClienteModel


class VendaModel(Base):
    """Vendas table."""

    __tablename__ = "vendas"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True)
    cliente_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    metodo_pagamento: Mapped[str] = mapped_column(String(32), nullable=False, default="pix")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pendente", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    cliente: Mapped[ClienteModel] = relationship(back_populates="vendas")
