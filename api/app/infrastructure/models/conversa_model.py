"""ORM mapping for conversas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.types import GUID

if TYPE_CHECKING:
    from app.infrastructure.models.cliente_model import ClienteModel


class ConversaModel(Base):
    """Conversas table."""

    __tablename__ = "conversas"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True)
    cliente_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    cliente: Mapped[ClienteModel] = relationship(back_populates="conversas")
