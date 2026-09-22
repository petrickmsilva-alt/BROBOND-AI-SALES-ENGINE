"""Aggregated v1 API router."""

from fastapi import APIRouter

from app.api.v1.routes import (
    auth,
    clientes,
    dashboard,
    health,
    leads,
    produtos,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(clientes.router)
api_router.include_router(produtos.router)
api_router.include_router(leads.router)
api_router.include_router(dashboard.router)
