"""Database seeding command.

Run with ``python -m app.seed`` (inside the API container or a configured
environment). Populates the CRM with representative BroBond data: customers,
the apparel catalogue, pipeline leads and a handful of sales.
"""

from __future__ import annotations

import asyncio
import logging
import random
from decimal import Decimal

from sqlalchemy import func, select

from app.core.logging import configure_logging
from app.domain.entities.cliente import Cliente
from app.domain.entities.conversa import Conversa, ConversaRole
from app.domain.entities.lead import Lead, LeadStatus
from app.domain.entities.produto import Produto
from app.domain.entities.venda import MetodoPagamento, Venda, VendaStatus
from app.infrastructure.db.session import dispose_engine, get_session_factory
from app.infrastructure.models.cliente_model import ClienteModel
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

logger = logging.getLogger("app.seed")

NUM_CLIENTES = 20
NUM_PRODUTOS = 30
NUM_LEADS = 50
NUM_VENDAS = 10

_FIRST_NAMES = [
    "Ana",
    "Bruno",
    "Carla",
    "Diego",
    "Eduarda",
    "Felipe",
    "Gabriela",
    "Henrique",
    "Isabela",
    "João",
    "Larissa",
    "Marcos",
    "Natália",
    "Otávio",
    "Paula",
    "Rafael",
    "Sofia",
    "Thiago",
    "Vanessa",
    "William",
]
_LAST_NAMES = [
    "Silva",
    "Souza",
    "Oliveira",
    "Santos",
    "Pereira",
    "Costa",
    "Almeida",
    "Ferreira",
    "Rodrigues",
    "Martins",
]
_CIDADES = [
    "Goiânia",
    "São Paulo",
    "Rio de Janeiro",
    "Belo Horizonte",
    "Curitiba",
    "Brasília",
    "Salvador",
    "Fortaleza",
]

_MODELOS = ["Camiseta Essential", "Oversized", "Polo", "Jeans", "Moletom"]
_CORES = ["Preto", "Branco", "Off White", "Verde Militar", "Azul Marinho"]
_TAMANHOS = ["P", "M", "G", "GG"]
_CATEGORIA_POR_MODELO = {
    "Camiseta Essential": "Camisetas",
    "Oversized": "Camisetas",
    "Polo": "Camisetas",
    "Jeans": "Calças",
    "Moletom": "Moletons",
}
_PRECO_BASE = {
    "Camiseta Essential": Decimal("89.90"),
    "Oversized": Decimal("119.90"),
    "Polo": Decimal("139.90"),
    "Jeans": Decimal("229.90"),
    "Moletom": Decimal("199.90"),
}

_ORIGENS = ["instagram", "whatsapp", "indicacao", "site", "loja"]
_INTERESSES = ["Camiseta Essential", "Oversized", "Polo", "Jeans", "Moletom", "Lançamento"]


def _build_produtos() -> list[Produto]:
    """Build the BroBond catalogue of exactly ``NUM_PRODUTOS`` SKUs.

    Combines every modelo with every cor (25 SKUs) and then adds size variants
    of the flagship models until the target count is reached, guaranteeing that
    all five models and all five colours appear.
    """
    produtos: list[Produto] = []
    index = 0

    def _add(modelo: str, cor: str, tamanho: str) -> None:
        nonlocal index
        index += 1
        slug_modelo = modelo.upper().replace(" ", "")[:6]
        slug_cor = cor.upper().replace(" ", "")[:3]
        sku = f"BB-{slug_modelo}-{slug_cor}-{index:03d}"
        produtos.append(
            Produto(
                sku=sku,
                nome=f"{modelo} {cor} {tamanho}",
                descricao=f"{modelo} BroBond na cor {cor}, tamanho {tamanho}.",
                categoria=_CATEGORIA_POR_MODELO[modelo],
                cor=cor,
                tamanho=tamanho,
                preco=_PRECO_BASE[modelo],
                estoque=random.randint(0, 120),
                ativo=True,
            )
        )

    for modelo in _MODELOS:
        for cor in _CORES:
            _add(modelo, cor, "M")

    # Top up with size variants to reach NUM_PRODUTOS.
    extra_sizes = [t for t in _TAMANHOS if t != "M"]
    combos = [(modelo, cor) for modelo in _MODELOS for cor in _CORES]
    combo_index = 0
    size_index = 0
    while index < NUM_PRODUTOS:
        modelo, cor = combos[combo_index % len(combos)]
        tamanho = extra_sizes[size_index % len(extra_sizes)]
        _add(modelo, cor, tamanho)
        combo_index += 1
        if combo_index % len(combos) == 0:
            size_index += 1

    return produtos


async def _already_seeded(session_factory: object) -> bool:
    async with session_factory() as session:  # type: ignore[operator]
        result = await session.execute(select(func.count()).select_from(ClienteModel))
        return int(result.scalar_one()) > 0


async def seed() -> None:
    """Populate the database with representative CRM data (idempotent)."""
    random.seed(42)
    session_factory = get_session_factory()

    if await _already_seeded(session_factory):
        logger.info("Database already contains clientes; skipping seed.")
        return

    async with session_factory() as session:
        clientes_repo = SQLAlchemyClienteRepository(session)
        produtos_repo = SQLAlchemyProdutoRepository(session)
        leads_repo = SQLAlchemyLeadRepository(session)
        vendas_repo = SQLAlchemyVendaRepository(session)
        conversas_repo = SQLAlchemyConversaRepository(session)

        clientes: list[Cliente] = []
        for i in range(NUM_CLIENTES):
            first = _FIRST_NAMES[i % len(_FIRST_NAMES)]
            last = random.choice(_LAST_NAMES)
            nome = f"{first} {last}"
            handle = f"{first}.{last}".lower()
            cliente = await clientes_repo.add(
                Cliente(
                    nome=nome,
                    telefone=f"+55 62 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    email=f"{handle}{i}@example.com",
                    instagram=f"@{handle}",
                    cidade=random.choice(_CIDADES),
                )
            )
            clientes.append(cliente)
        logger.info("Inserted %d clientes.", len(clientes))

        produtos = 0
        for produto in _build_produtos():
            await produtos_repo.add(produto)
            produtos += 1
        logger.info("Inserted %d produtos.", produtos)

        statuses: list[LeadStatus] = list(LeadStatus)
        for i in range(NUM_LEADS):
            cliente = random.choice(clientes)
            await leads_repo.add(
                Lead(
                    cliente_id=cliente.id,
                    origem=random.choice(_ORIGENS),
                    score=random.randint(0, 100),
                    status=statuses[i % len(statuses)],
                    interesse=random.choice(_INTERESSES),
                    observacao="Lead gerado pelo seed.",
                )
            )
        logger.info("Inserted %d leads.", NUM_LEADS)

        metodos: list[MetodoPagamento] = list(MetodoPagamento)
        venda_statuses: list[VendaStatus] = [VendaStatus.PAGO, VendaStatus.PENDENTE]
        for _ in range(NUM_VENDAS):
            cliente = random.choice(clientes)
            await vendas_repo.add(
                Venda(
                    cliente_id=cliente.id,
                    valor=Decimal(str(random.randint(90, 800))) + Decimal("0.90"),
                    metodo_pagamento=random.choice(metodos),
                    status=random.choice(venda_statuses),
                )
            )
        logger.info("Inserted %d vendas.", NUM_VENDAS)

        for cliente in clientes[:5]:
            await conversas_repo.add(
                Conversa(
                    cliente_id=cliente.id,
                    role=ConversaRole.USER,
                    mensagem="Oi! Vi o lançamento de vocês no Instagram.",
                )
            )
            await conversas_repo.add(
                Conversa(
                    cliente_id=cliente.id,
                    role=ConversaRole.ASSISTANT,
                    mensagem="Olá! Que bom te ver por aqui. Posso te ajudar com um tamanho?",
                )
            )
        logger.info("Inserted sample conversas.")


async def _main() -> None:
    configure_logging(debug=False)
    try:
        await seed()
        logger.info("Seed completed.")
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(_main())
