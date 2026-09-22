"""SQLAlchemy adapter for the produto repository port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.produto import Produto
from app.domain.repositories.produto_repository import ProdutoRepository
from app.infrastructure.models.produto_model import ProdutoModel


def _to_entity(model: ProdutoModel) -> Produto:
    return Produto(
        id=model.id,
        sku=model.sku,
        nome=model.nome,
        descricao=model.descricao,
        categoria=model.categoria,
        cor=model.cor,
        tamanho=model.tamanho,
        preco=model.preco,
        estoque=model.estoque,
        ativo=model.ativo,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SQLAlchemyProdutoRepository(ProdutoRepository):
    """Persists produtos in PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, produto: Produto) -> Produto:
        """Persist a new produto."""
        model = ProdutoModel(
            id=produto.id,
            sku=produto.sku,
            nome=produto.nome,
            descricao=produto.descricao,
            categoria=produto.categoria,
            cor=produto.cor,
            tamanho=produto.tamanho,
            preco=produto.preco,
            estoque=produto.estoque,
            ativo=produto.ativo,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(self, produto: Produto) -> Produto:
        """Persist changes to an existing produto."""
        model = await self._session.get(ProdutoModel, produto.id)
        if model is None:
            raise LookupError(f"Produto {produto.id} not found")
        model.sku = produto.sku
        model.nome = produto.nome
        model.descricao = produto.descricao
        model.categoria = produto.categoria
        model.cor = produto.cor
        model.tamanho = produto.tamanho
        model.preco = produto.preco
        model.estoque = produto.estoque
        model.ativo = produto.ativo
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def get_by_id(self, produto_id: UUID) -> Produto | None:
        """Return a produto by identifier, if present."""
        model = await self._session.get(ProdutoModel, produto_id)
        return _to_entity(model) if model else None

    async def get_by_sku(self, sku: str) -> Produto | None:
        """Return a produto by its SKU, if present."""
        result = await self._session.execute(select(ProdutoModel).where(ProdutoModel.sku == sku))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Produto]:
        """Return a page of produtos."""
        result = await self._session.execute(
            select(ProdutoModel).order_by(ProdutoModel.nome).limit(limit).offset(offset)
        )
        return [_to_entity(model) for model in result.scalars().all()]

    async def count(self) -> int:
        """Return the total number of produtos."""
        result = await self._session.execute(select(func.count()).select_from(ProdutoModel))
        return int(result.scalar_one())

    async def delete(self, produto_id: UUID) -> bool:
        """Delete a produto, returning True when a row was removed."""
        result = await self._session.execute(
            delete(ProdutoModel).where(ProdutoModel.id == produto_id)
        )
        await self._session.commit()
        return bool(result.rowcount)
