"""Tests for the database seed command."""

from __future__ import annotations

import pytest

from app import seed as seed_module
from app.infrastructure.db import session as db_session
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
async def test_seed_populates_expected_volumes(isolated_db: None) -> None:
    await seed_module.seed()

    factory = db_session.get_session_factory()
    async with factory() as session:
        clientes = await SQLAlchemyClienteRepository(session).count()
        produtos = await SQLAlchemyProdutoRepository(session).count()
        leads = await SQLAlchemyLeadRepository(session).count()
        vendas = await SQLAlchemyVendaRepository(session).count()
        conversas = await SQLAlchemyConversaRepository(session).count()

    assert clientes == seed_module.NUM_CLIENTES
    assert produtos == seed_module.NUM_PRODUTOS
    assert leads == seed_module.NUM_LEADS
    assert vendas == seed_module.NUM_VENDAS
    assert conversas > 0


@pytest.mark.asyncio
async def test_seed_is_idempotent(isolated_db: None) -> None:
    # A second run must not duplicate data.
    await seed_module.seed()
    await seed_module.seed()

    factory = db_session.get_session_factory()
    async with factory() as session:
        clientes = await SQLAlchemyClienteRepository(session).count()

    assert clientes == seed_module.NUM_CLIENTES


@pytest.mark.asyncio
async def test_seed_builds_expected_catalogue() -> None:
    produtos = seed_module._build_produtos()
    assert len(produtos) == seed_module.NUM_PRODUTOS
    nomes = " ".join(p.nome for p in produtos)
    for modelo in ["Camiseta Essential", "Oversized", "Polo", "Jeans", "Moletom"]:
        assert modelo in nomes
    cores = {p.cor for p in produtos}
    for cor in ["Preto", "Branco", "Off White", "Verde Militar", "Azul Marinho"]:
        assert cor in cores
