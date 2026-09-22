"""Unit tests for the application service layer using real repositories."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.application.services.cliente_service import ClienteService
from app.application.services.dashboard_service import DashboardService
from app.application.services.lead_service import LeadService
from app.application.services.produto_service import ProdutoService
from app.core.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from app.domain.entities.lead import LeadStatus
from app.domain.repositories.ai_gateway import AIGateway, LeadScoreResult
from app.infrastructure.repositories.sqlalchemy_cliente_repository import (
    SQLAlchemyClienteRepository,
)
from app.infrastructure.repositories.sqlalchemy_lead_repository import SQLAlchemyLeadRepository
from app.infrastructure.repositories.sqlalchemy_produto_repository import (
    SQLAlchemyProdutoRepository,
)
from app.infrastructure.repositories.sqlalchemy_venda_repository import SQLAlchemyVendaRepository


class StubAIGateway(AIGateway):
    """Deterministic AI gateway for tests."""

    def __init__(self, score: int = 75, rationale: str = "Great fit") -> None:
        self._score = score
        self._rationale = rationale

    async def health(self) -> bool:
        return True

    async def score_lead(self, prompt: str) -> LeadScoreResult:
        return LeadScoreResult(score=self._score, rationale=self._rationale)


@pytest.mark.asyncio
async def test_cliente_service_crud(session) -> None:
    service = ClienteService(SQLAlchemyClienteRepository(session))
    cliente = await service.create(nome="Ana", cidade="Goiânia")

    fetched = await service.get(cliente.id)
    assert fetched.nome == "Ana"

    updated = await service.update(cliente.id, nome="Ana Paula", telefone="123")
    assert updated.nome == "Ana Paula"
    assert updated.telefone == "123"

    items, total = await service.list_clientes()
    assert total >= 1
    assert any(c.id == cliente.id for c in items)

    await service.delete(cliente.id)
    with pytest.raises(EntityNotFoundError):
        await service.get(cliente.id)


@pytest.mark.asyncio
async def test_cliente_service_delete_missing(session) -> None:
    service = ClienteService(SQLAlchemyClienteRepository(session))
    with pytest.raises(EntityNotFoundError):
        await service.delete(__import__("uuid").UUID("00000000-0000-0000-0000-000000000000"))


@pytest.mark.asyncio
async def test_produto_service_crud_and_uniqueness(session) -> None:
    service = ProdutoService(SQLAlchemyProdutoRepository(session))
    produto = await service.create(sku="SKU-A", nome="Camiseta", preco=Decimal("50"))

    with pytest.raises(EntityAlreadyExistsError):
        await service.create(sku="SKU-A", nome="Outra", preco=Decimal("10"))

    other = await service.create(sku="SKU-B", nome="Polo", preco=Decimal("70"))
    with pytest.raises(EntityAlreadyExistsError):
        await service.update(other.id, sku="SKU-A")

    updated = await service.update(
        produto.id,
        nome="Camiseta Nova",
        descricao="desc",
        categoria="cat",
        cor="Preto",
        tamanho="M",
        preco=Decimal("55"),
        estoque=5,
        ativo=False,
    )
    assert updated.nome == "Camiseta Nova"
    assert updated.preco == Decimal("55")
    assert updated.ativo is False

    items, total = await service.list_produtos()
    assert total >= 2
    assert any(p.id == produto.id for p in items)

    await service.delete(produto.id)
    with pytest.raises(EntityNotFoundError):
        await service.get(produto.id)


@pytest.mark.asyncio
async def test_produto_service_errors(session) -> None:
    service = ProdutoService(SQLAlchemyProdutoRepository(session))
    ghost = __import__("uuid").UUID("00000000-0000-0000-0000-000000000000")
    with pytest.raises(EntityNotFoundError):
        await service.get(ghost)
    with pytest.raises(EntityNotFoundError):
        await service.update(ghost, nome="X")
    with pytest.raises(EntityNotFoundError):
        await service.delete(ghost)


@pytest.mark.asyncio
async def test_lead_service_qualify_scores_lead(session) -> None:
    clientes = SQLAlchemyClienteRepository(session)
    leads = SQLAlchemyLeadRepository(session)
    cliente_service = ClienteService(clientes)
    lead_service = LeadService(leads, clientes, StubAIGateway(score=90))

    cliente = await cliente_service.create(nome="Score Me")
    lead = await lead_service.create(cliente_id=cliente.id, origem="site")
    qualified = await lead_service.qualify(lead.id)

    assert qualified.score == 90
    assert qualified.status is LeadStatus.CONTATO


@pytest.mark.asyncio
async def test_lead_service_create_requires_cliente(session) -> None:
    clientes = SQLAlchemyClienteRepository(session)
    leads = SQLAlchemyLeadRepository(session)
    service = LeadService(leads, clientes, StubAIGateway())
    ghost = __import__("uuid").UUID("00000000-0000-0000-0000-000000000000")
    with pytest.raises(EntityNotFoundError):
        await service.create(cliente_id=ghost)
    with pytest.raises(EntityNotFoundError):
        await service.get(ghost)
    with pytest.raises(EntityNotFoundError):
        await service.change_status(ghost, LeadStatus.FECHADO)


@pytest.mark.asyncio
async def test_dashboard_service_summary(session) -> None:
    clientes = SQLAlchemyClienteRepository(session)
    produtos = SQLAlchemyProdutoRepository(session)
    leads = SQLAlchemyLeadRepository(session)
    vendas = SQLAlchemyVendaRepository(session)
    service = DashboardService(clientes, produtos, leads, vendas)

    summary = await service.summary()
    assert summary.clientes >= 0
    assert summary.pipeline.novo >= 0
    assert summary.receita >= Decimal("0")
