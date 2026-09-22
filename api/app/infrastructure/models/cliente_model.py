"""ORM mapping for clientes."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.types import GUID

if TYPE_CHECKING:
    from app.infrastructure.models.conversa_model import ConversaModel
    from app.infrastructure.models.lead_model import LeadModel
    from app.infrastructure.models.venda_model import VendaModel


class ClienteModel(Base):
    """Clientes table."""

    __tablename__ = "clientes"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    telefone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True, index=True)
    instagram: Mapped[str | None] = mapped_column(String(128), nullable=True)
    cidade: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    leads: Mapped[list[LeadModel]] = relationship(
        back_populates="cliente", cascade="all, delete-orphan", passive_deletes=True
    )
    conversas: Mapped[list[ConversaModel]] = relationship(
        back_populates="cliente", cascade="all, delete-orphan", passive_deletes=True
    )
    vendas: Mapped[list[VendaModel]] = relationship(
        back_populates="cliente", cascade="all, delete-orphan", passive_deletes=True
    )
