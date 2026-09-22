"""Use cases for cliente management."""

from __future__ import annotations

from uuid import UUID

from app.core.exceptions import EntityNotFoundError
from app.domain.entities.cliente import Cliente
from app.domain.repositories.cliente_repository import ClienteRepository


class ClienteService:
    """Coordinates cliente persistence and business rules."""

    def __init__(self, clientes: ClienteRepository) -> None:
        self._clientes = clientes

    async def create(
        self,
        nome: str,
        telefone: str | None = None,
        email: str | None = None,
        instagram: str | None = None,
        cidade: str | None = None,
    ) -> Cliente:
        """Register a new cliente."""
        cliente = Cliente(
            nome=nome,
            telefone=telefone,
            email=email,
            instagram=instagram,
            cidade=cidade,
        )
        return await self._clientes.add(cliente)

    async def list_clientes(self, limit: int = 50, offset: int = 0) -> tuple[list[Cliente], int]:
        """Return a page of clientes and the total count."""
        items = await self._clientes.list_all(limit=limit, offset=offset)
        total = await self._clientes.count()
        return items, total

    async def get(self, cliente_id: UUID) -> Cliente:
        """Return a cliente or raise when missing."""
        cliente = await self._clientes.get_by_id(cliente_id)
        if cliente is None:
            raise EntityNotFoundError(f"Cliente {cliente_id} not found")
        return cliente

    async def update(
        self,
        cliente_id: UUID,
        *,
        nome: str | None = None,
        telefone: str | None = None,
        email: str | None = None,
        instagram: str | None = None,
        cidade: str | None = None,
    ) -> Cliente:
        """Apply a partial update to a cliente."""
        cliente = await self.get(cliente_id)
        if nome is not None:
            cliente.nome = nome
        if telefone is not None:
            cliente.telefone = telefone
        if email is not None:
            cliente.email = email
        if instagram is not None:
            cliente.instagram = instagram
        if cidade is not None:
            cliente.cidade = cidade
        cliente.touch()
        return await self._clientes.update(cliente)

    async def delete(self, cliente_id: UUID) -> None:
        """Remove a cliente, raising when it does not exist."""
        deleted = await self._clientes.delete(cliente_id)
        if not deleted:
            raise EntityNotFoundError(f"Cliente {cliente_id} not found")
