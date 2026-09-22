"""ORM mapping for leads."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.types import GUID

if TYPE_CHECKING:
    from app.infrastructure.models.cliente_model import ClienteModel


class LeadModel(Base):
    """Leads table."""

    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True)
    cliente_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    origem: Mapped[str | None] = mapped_column(String(64), nullable=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="novo", index=True)
    interesse: Mapped[str | None] = mapped_column(String(255), nullable=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    cliente: Mapped[ClienteModel] = relationship(back_populates="leads")
