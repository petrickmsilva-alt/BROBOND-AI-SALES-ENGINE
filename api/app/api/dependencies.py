"""FastAPI dependency wiring (composition root)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.auth_service import AuthService
from app.application.services.cliente_service import ClienteService
from app.application.services.dashboard_service import DashboardService
from app.application.services.health_service import HealthService
from app.application.services.lead_service import LeadService
from app.application.services.produto_service import ProdutoService
from app.core.config import Settings, get_settings
from app.core.security import TokenError, decode_token
from app.domain.entities.user import User
from app.domain.repositories.ai_gateway import AIGateway
from app.domain.repositories.cliente_repository import ClienteRepository
from app.domain.repositories.lead_repository import LeadRepository
from app.domain.repositories.produto_repository import ProdutoRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.venda_repository import VendaRepository
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.db.session import get_session
from app.infrastructure.llm.ollama_gateway import OllamaGateway
from app.infrastructure.repositories.sqlalchemy_cliente_repository import (
    SQLAlchemyClienteRepository,
)
from app.infrastructure.repositories.sqlalchemy_lead_repository import SQLAlchemyLeadRepository
from app.infrastructure.repositories.sqlalchemy_produto_repository import (
    SQLAlchemyProdutoRepository,
)
from app.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.infrastructure.repositories.sqlalchemy_venda_repository import SQLAlchemyVendaRepository

_bearer_scheme = HTTPBearer(auto_error=False)

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
RedisDep = Annotated[Redis, Depends(get_redis)]


def get_ai_gateway(settings: SettingsDep) -> AIGateway:
    """Provide the configured AI gateway."""
    return OllamaGateway(settings)


AIGatewayDep = Annotated[AIGateway, Depends(get_ai_gateway)]


def get_user_repository(session: SessionDep) -> UserRepository:
    """Provide the user repository adapter."""
    return SQLAlchemyUserRepository(session)


def get_cliente_repository(session: SessionDep) -> ClienteRepository:
    """Provide the cliente repository adapter."""
    return SQLAlchemyClienteRepository(session)


def get_produto_repository(session: SessionDep) -> ProdutoRepository:
    """Provide the produto repository adapter."""
    return SQLAlchemyProdutoRepository(session)


def get_lead_repository(session: SessionDep) -> LeadRepository:
    """Provide the lead repository adapter."""
    return SQLAlchemyLeadRepository(session)


def get_venda_repository(session: SessionDep) -> VendaRepository:
    """Provide the venda repository adapter."""
    return SQLAlchemyVendaRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
ClienteRepositoryDep = Annotated[ClienteRepository, Depends(get_cliente_repository)]
ProdutoRepositoryDep = Annotated[ProdutoRepository, Depends(get_produto_repository)]
LeadRepositoryDep = Annotated[LeadRepository, Depends(get_lead_repository)]
VendaRepositoryDep = Annotated[VendaRepository, Depends(get_venda_repository)]


def get_auth_service(users: UserRepositoryDep) -> AuthService:
    """Provide the auth use cases."""
    return AuthService(users)


def get_cliente_service(clientes: ClienteRepositoryDep) -> ClienteService:
    """Provide the cliente use cases."""
    return ClienteService(clientes)


def get_produto_service(produtos: ProdutoRepositoryDep) -> ProdutoService:
    """Provide the produto use cases."""
    return ProdutoService(produtos)


def get_lead_service(
    leads: LeadRepositoryDep,
    clientes: ClienteRepositoryDep,
    ai_gateway: AIGatewayDep,
) -> LeadService:
    """Provide the lead use cases."""
    return LeadService(leads, clientes, ai_gateway)


def get_dashboard_service(
    clientes: ClienteRepositoryDep,
    produtos: ProdutoRepositoryDep,
    leads: LeadRepositoryDep,
    vendas: VendaRepositoryDep,
) -> DashboardService:
    """Provide the dashboard use cases."""
    return DashboardService(clientes, produtos, leads, vendas)


def get_health_service(
    settings: SettingsDep,
    session: SessionDep,
    redis: RedisDep,
    ai_gateway: AIGatewayDep,
) -> HealthService:
    """Provide the health use case."""
    return HealthService(settings=settings, session=session, redis=redis, ai_gateway=ai_gateway)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
ClienteServiceDep = Annotated[ClienteService, Depends(get_cliente_service)]
ProdutoServiceDep = Annotated[ProdutoService, Depends(get_produto_service)]
LeadServiceDep = Annotated[LeadService, Depends(get_lead_service)]
DashboardServiceDep = Annotated[DashboardService, Depends(get_dashboard_service)]
HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]


async def get_current_user(
    users: UserRepositoryDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)] = None,
) -> User:
    """Resolve the authenticated user from the bearer token."""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    try:
        claims = decode_token(credentials.credentials, "access")
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user = await users.get_by_id(UUID(str(claims["sub"])))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
