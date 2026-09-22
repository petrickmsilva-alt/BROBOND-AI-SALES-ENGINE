"""Domain rule tests."""

from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.entities.cliente import Cliente
from app.domain.entities.lead import Lead, LeadStatus
from app.domain.entities.produto import Produto
from app.domain.entities.venda import Venda


def test_lead_apply_score_promotes_new_lead() -> None:
    lead = Lead(cliente_id=uuid4())
    lead.apply_score(80, "Strong interest")
    assert lead.status is LeadStatus.CONTATO
    assert lead.score == 80
    assert lead.observacao == "Strong interest"


def test_lead_apply_score_rejects_out_of_range() -> None:
    lead = Lead(cliente_id=uuid4())
    with pytest.raises(ValueError, match="between 0 and 100"):
        lead.apply_score(150)


def test_lead_change_status() -> None:
    lead = Lead(cliente_id=uuid4())
    lead.change_status(LeadStatus.FECHADO)
    assert lead.status is LeadStatus.FECHADO


def test_produto_coerces_and_validates_preco() -> None:
    produto = Produto(sku="X-1", nome="Camiseta", preco="99.90")  # type: ignore[arg-type]
    assert produto.preco == Decimal("99.90")
    with pytest.raises(ValueError, match="negative"):
        Produto(sku="X-2", nome="Camiseta", preco=Decimal("-1"))


def test_produto_reduce_stock() -> None:
    produto = Produto(sku="X-3", nome="Jeans", preco=Decimal("1"), estoque=5)
    produto.reduce_stock(3)
    assert produto.estoque == 2
    with pytest.raises(ValueError, match="Insufficient stock"):
        produto.reduce_stock(10)


def test_venda_rejects_negative_valor() -> None:
    with pytest.raises(ValueError, match="negative"):
        Venda(cliente_id=uuid4(), valor=Decimal("-5"))


def test_cliente_touch_updates_timestamp() -> None:
    cliente = Cliente(nome="Ana")
    before = cliente.updated_at
    cliente.touch()
    assert cliente.updated_at >= before
