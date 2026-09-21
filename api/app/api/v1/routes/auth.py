"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import AuthServiceDep, CurrentUserDep
from app.application.dto.auth_dto import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.core.exceptions import AuthenticationError, EntityAlreadyExistsError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an account",
)
async def register(payload: RegisterRequest, service: AuthServiceDep) -> UserResponse:
    """Register a new user."""
    try:
        user = await service.register(
            email=str(payload.email),
            full_name=payload.full_name,
            password=payload.password,
            role=payload.role,
        )
    except EntityAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )


@router.post("/login", response_model=TokenResponse, summary="Exchange credentials for tokens")
async def login(payload: LoginRequest, service: AuthServiceDep) -> TokenResponse:
    """Authenticate and issue a JWT pair."""
    try:
        access, refresh = await service.authenticate(str(payload.email), payload.password)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.get("/me", response_model=UserResponse, summary="Current authenticated user")
async def me(current_user: CurrentUserDep) -> UserResponse:
    """Return the profile bound to the bearer token."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
    )
