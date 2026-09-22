"""Produto endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import ProdutoServiceDep
from app.application.dto.produto_dto import (
    ProdutoCreateRequest,
    ProdutoListResponse,
    ProdutoResponse,
    ProdutoUpdateRequest,
)
from app.core.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from app.domain.entities.produto import Produto

router = APIRouter(prefix="/produtos", tags=["produtos"])


def _to_response(produto: Produto) -> ProdutoResponse:
    return ProdutoResponse(
        id=str(produto.id),
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


@router.get("", response_model=ProdutoListResponse, summary="List produtos")
async def list_produtos(
    service: ProdutoServiceDep,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> ProdutoListResponse:
    """Return a page of produtos."""
    items, total = await service.list_produtos(limit=limit, offset=offset)
    return ProdutoListResponse(total=total, items=[_to_response(p) for p in items])


@router.get("/{produto_id}", response_model=ProdutoResponse, summary="Get a produto")
async def get_produto(produto_id: UUID, service: ProdutoServiceDep) -> ProdutoResponse:
    """Return a single produto."""
    try:
        produto = await service.get(produto_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_response(produto)


@router.post(
    "",
    response_model=ProdutoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a produto",
)
async def create_produto(
    payload: ProdutoCreateRequest, service: ProdutoServiceDep
) -> ProdutoResponse:
    """Register a new produto."""
    try:
        produto = await service.create(
            sku=payload.sku,
            nome=payload.nome,
            preco=payload.preco,
            descricao=payload.descricao,
            categoria=payload.categoria,
            cor=payload.cor,
            tamanho=payload.tamanho,
            estoque=payload.estoque,
            ativo=payload.ativo,
        )
    except EntityAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_response(produto)


@router.put("/{produto_id}", response_model=ProdutoResponse, summary="Update a produto")
async def update_produto(
    produto_id: UUID, payload: ProdutoUpdateRequest, service: ProdutoServiceDep
) -> ProdutoResponse:
    """Apply a partial update to a produto."""
    try:
        produto = await service.update(
            produto_id,
            sku=payload.sku,
            nome=payload.nome,
            descricao=payload.descricao,
            categoria=payload.categoria,
            cor=payload.cor,
            tamanho=payload.tamanho,
            preco=payload.preco,
            estoque=payload.estoque,
            ativo=payload.ativo,
        )
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EntityAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_response(produto)
