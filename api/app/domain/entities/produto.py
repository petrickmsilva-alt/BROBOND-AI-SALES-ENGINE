"""Produto aggregate."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass(slots=True)
class Produto:
    """A product from the BroBond catalogue."""

    sku: str
    nome: str
    preco: Decimal
    descricao: str | None = None
    categoria: str | None = None
    cor: str | None = None
    tamanho: str | None = None
    estoque: int = 0
    ativo: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not isinstance(self.preco, Decimal):
            self.preco = Decimal(str(self.preco))
        if self.preco < 0:
            raise ValueError("Produto preco must not be negative")
        if self.estoque < 0:
            raise ValueError("Produto estoque must not be negative")

    def reduce_stock(self, quantity: int) -> None:
        """Decrease available stock, guarding against overselling."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if quantity > self.estoque:
            raise ValueError("Insufficient stock")
        self.estoque -= quantity
        self.updated_at = datetime.now(UTC)
