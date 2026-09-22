"""Unit tests for repository adapters covering less-common paths."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.domain.entities.cliente import Cliente
from app.domain.entities.conversa import Conversa, ConversaRole
from app.domain.entities.lead import Lead, LeadStatus
from app.domain.entities.venda import MetodoPagamento, Venda, VendaStatus
from app.infrastructure.repositories.sqlalchemy_cliente_repository import (
    SQLAlchemyClienteRepository,
)
from app.infrastructure.repositories.sqlalchemy_conversa_repository import (
    SQLAlchemyConversaRepository,
)
from app.infrastructure.repositories.sqlalchemy_lead_repository import SQLAlchemyLeadRepository
from app.infrastructure.repositories.sqlalchemy_produto_repository import (
    SQLAlchemyProdutoRepository,
)
from app.infrastructure.repositories.sqlalchemy_venda_repository import SQLAlchemyVendaRepository


@pytest.mark.asyncio
async def test_venda_total_revenue_counts_only_paid(session) -> None:
    clientes = SQLAlchemyClienteRepository(session)
    vendas = SQLAlchemyVendaRepository(session)
    cliente = await clientes.add(Cliente(nome="Rev"))

    await vendas.add(
        Venda(
            cliente_id=cliente.id,
            valor=Decimal("100.00"),
            metodo_pagamento=MetodoPagamento.PIX,
            status=VendaStatus.PAGO,
        )
    )
    await vendas.add(
        Venda(
            cliente_id=cliente.id,
            valor=Decimal("50.00"),
            status=VendaStatus.PENDENTE,
        )
    )
    revenue = await vendas.total_revenue()
    assert revenue >= Decimal("100.00")

    listed = await vendas.list_all()
    assert len(listed) >= 2
    fetched = await vendas.get_by_id(listed[0].id)
    assert fetched is not None


@pytest.mark.asyncio
async def test_lead_count_by_status_covers_all_stages(session) -> None:
    clientes = SQLAlchemyClienteRepository(session)
    leads = SQLAlchemyLeadRepository(session)
    cliente = await clientes.add(Cliente(nome="Counts"))

    for status in LeadStatus:
        await leads.add(Lead(cliente_id=cliente.id, status=status))

    counts = await leads.count_by_status()
    assert set(counts.keys()) == set(LeadStatus)
    assert all(counts[status] >= 1 for status in LeadStatus)


@pytest.mark.asyncio
async def test_lead_update_and_delete(session) -> None:
    clientes = SQLAlchemyClienteRepository(session)
    leads = SQLAlchemyLeadRepository(session)
    cliente = await clientes.add(Cliente(nome="Upd"))
    lead = await leads.add(Lead(cliente_id=cliente.id, origem="site"))

    lead.origem = "instagram"
    lead.status = LeadStatus.PROPOSTA
    updated = await leads.update(lead)
    assert updated.origem == "instagram"
    assert updated.status is LeadStatus.PROPOSTA

    assert await leads.delete(lead.id) is True
    assert await leads.get_by_id(lead.id) is None


@pytest.mark.asyncio
async def test_lead_update_missing_raises(session) -> None:
    leads = SQLAlchemyLeadRepository(session)
    with pytest.raises(LookupError):
        await leads.update(Lead(cliente_id=__import__("uuid").uuid4()))


@pytest.mark.asyncio
async def test_produto_get_by_sku_and_missing_update(session) -> None:
    produtos = SQLAlchemyProdutoRepository(session)
    with pytest.raises(LookupError):
        from app.domain.entities.produto import Produto

        await produtos.update(Produto(sku="ghost", nome="G", preco=Decimal("1")))
    assert await produtos.get_by_sku("nonexistent") is None


@pytest.mark.asyncio
async def test_cliente_update_missing_raises(session) -> None:
    clientes = SQLAlchemyClienteRepository(session)
    with pytest.raises(LookupError):
        await clientes.update(Cliente(nome="ghost"))


@pytest.mark.asyncio
async def test_conversa_history(session) -> None:
    clientes = SQLAlchemyClienteRepository(session)
    conversas = SQLAlchemyConversaRepository(session)
    cliente = await clientes.add(Cliente(nome="Chat"))

    await conversas.add(Conversa(cliente_id=cliente.id, role=ConversaRole.USER, mensagem="Oi"))
    await conversas.add(
        Conversa(cliente_id=cliente.id, role=ConversaRole.ASSISTANT, mensagem="Olá")
    )
    history = await conversas.list_by_cliente(cliente.id)
    assert len(history) == 2
    assert history[0].role is ConversaRole.USER
    assert await conversas.count() >= 2
