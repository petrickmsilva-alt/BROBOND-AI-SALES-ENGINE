"""Cliente endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.api.dependencies import ClienteServiceDep
from app.application.dto.cliente_dto import (
    ClienteCreateRequest,
    ClienteListResponse,
    ClienteResponse,
    ClienteUpdateRequest,
)
from app.core.exceptions import EntityNotFoundError
from app.domain.entities.cliente import Cliente

router = APIRouter(prefix="/clientes", tags=["clientes"])


def _to_response(cliente: Cliente) -> ClienteResponse:
    return ClienteResponse(
        id=str(cliente.id),
        nome=cliente.nome,
        telefone=cliente.telefone,
        email=cliente.email,
        instagram=cliente.instagram,
        cidade=cliente.cidade,
        created_at=cliente.created_at,
        updated_at=cliente.updated_at,
    )


@router.get("", response_model=ClienteListResponse, summary="List clientes")
async def list_clientes(
    service: ClienteServiceDep,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> ClienteListResponse:
    """Return a page of clientes."""
    items, total = await service.list_clientes(limit=limit, offset=offset)
    return ClienteListResponse(total=total, items=[_to_response(c) for c in items])


@router.get("/{cliente_id}", response_model=ClienteResponse, summary="Get a cliente")
async def get_cliente(cliente_id: UUID, service: ClienteServiceDep) -> ClienteResponse:
    """Return a single cliente."""
    try:
        cliente = await service.get(cliente_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_response(cliente)


@router.post(
    "",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a cliente",
)
async def create_cliente(
    payload: ClienteCreateRequest, service: ClienteServiceDep
) -> ClienteResponse:
    """Register a new cliente."""
    cliente = await service.create(
        nome=payload.nome,
        telefone=payload.telefone,
        email=str(payload.email) if payload.email else None,
        instagram=payload.instagram,
        cidade=payload.cidade,
    )
    return _to_response(cliente)


@router.put("/{cliente_id}", response_model=ClienteResponse, summary="Update a cliente")
async def update_cliente(
    cliente_id: UUID, payload: ClienteUpdateRequest, service: ClienteServiceDep
) -> ClienteResponse:
    """Apply a partial update to a cliente."""
    try:
        cliente = await service.update(
            cliente_id,
            nome=payload.nome,
            telefone=payload.telefone,
            email=str(payload.email) if payload.email else None,
            instagram=payload.instagram,
            cidade=payload.cidade,
        )
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_response(cliente)


@router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a cliente",
)
async def delete_cliente(cliente_id: UUID, service: ClienteServiceDep) -> Response:
    """Remove a cliente and its related records."""
    try:
        await service.delete(cliente_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
