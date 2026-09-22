"""Use cases for produto management."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from app.core.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from app.domain.entities.produto import Produto
from app.domain.repositories.produto_repository import ProdutoRepository


class ProdutoService:
    """Coordinates produto persistence and business rules."""

    def __init__(self, produtos: ProdutoRepository) -> None:
        self._produtos = produtos

    async def create(
        self,
        sku: str,
        nome: str,
        preco: Decimal,
        descricao: str | None = None,
        categoria: str | None = None,
        cor: str | None = None,
        tamanho: str | None = None,
        estoque: int = 0,
        ativo: bool = True,
    ) -> Produto:
        """Register a new produto, enforcing SKU uniqueness."""
        if await self._produtos.get_by_sku(sku) is not None:
            raise EntityAlreadyExistsError(f"Produto with SKU {sku} already exists")
        produto = Produto(
            sku=sku,
            nome=nome,
            preco=preco,
            descricao=descricao,
            categoria=categoria,
            cor=cor,
            tamanho=tamanho,
            estoque=estoque,
            ativo=ativo,
        )
        return await self._produtos.add(produto)

    async def list_produtos(self, limit: int = 50, offset: int = 0) -> tuple[list[Produto], int]:
        """Return a page of produtos and the total count."""
        items = await self._produtos.list_all(limit=limit, offset=offset)
        total = await self._produtos.count()
        return items, total

    async def get(self, produto_id: UUID) -> Produto:
        """Return a produto or raise when missing."""
        produto = await self._produtos.get_by_id(produto_id)
        if produto is None:
            raise EntityNotFoundError(f"Produto {produto_id} not found")
        return produto

    async def update(
        self,
        produto_id: UUID,
        *,
        sku: str | None = None,
        nome: str | None = None,
        descricao: str | None = None,
        categoria: str | None = None,
        cor: str | None = None,
        tamanho: str | None = None,
        preco: Decimal | None = None,
        estoque: int | None = None,
        ativo: bool | None = None,
    ) -> Produto:
        """Apply a partial update to a produto."""
        produto = await self.get(produto_id)
        if sku is not None and sku != produto.sku:
            existing = await self._produtos.get_by_sku(sku)
            if existing is not None and existing.id != produto.id:
                raise EntityAlreadyExistsError(f"Produto with SKU {sku} already exists")
            produto.sku = sku
        if nome is not None:
            produto.nome = nome
        if descricao is not None:
            produto.descricao = descricao
        if categoria is not None:
            produto.categoria = categoria
        if cor is not None:
            produto.cor = cor
        if tamanho is not None:
            produto.tamanho = tamanho
        if preco is not None:
            produto.preco = preco if isinstance(preco, Decimal) else Decimal(str(preco))
        if estoque is not None:
            produto.estoque = estoque
        if ativo is not None:
            produto.ativo = ativo
        return await self._produtos.update(produto)

    async def delete(self, produto_id: UUID) -> None:
        """Remove a produto, raising when it does not exist."""
        deleted = await self._produtos.delete(produto_id)
        if not deleted:
            raise EntityNotFoundError(f"Produto {produto_id} not found")
