"""Venda aggregate."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4


class VendaStatus(StrEnum):
    """Lifecycle of a sale."""

    PENDENTE = "pendente"
    PAGO = "pago"
    CANCELADO = "cancelado"


class MetodoPagamento(StrEnum):
    """Accepted payment methods."""

    PIX = "pix"
    CARTAO = "cartao"
    BOLETO = "boleto"
    DINHEIRO = "dinheiro"


@dataclass(slots=True)
class Venda:
    """A sale closed for a customer."""

    cliente_id: UUID
    valor: Decimal
    metodo_pagamento: MetodoPagamento = MetodoPagamento.PIX
    status: VendaStatus = VendaStatus.PENDENTE
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not isinstance(self.valor, Decimal):
            self.valor = Decimal(str(self.valor))
        if self.valor < 0:
            raise ValueError("Venda valor must not be negative")
