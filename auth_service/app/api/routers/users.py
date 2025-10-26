# pylint:disable=bad-exception-cause,catching-non-exception,unused-argument
# ruff:noqa:E712
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from pydantic import Field

from auth_service.app.auth.dependencies import get_user_service
from auth_service.app.auth.security import (
    create_access_token,
    create_refresh_token,
    get_email_current_user,
)
from auth_service.app.core.exceptions import ConflictException, NotFoundException
from auth_service.app.core.limiter import limiter
from auth_service.app.schemas.tokens import RefreshTokenRequest, TokenGroup
from auth_service.app.schemas.users import User, UserCreate
from auth_service.app.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])

REQUEST_TOTAL = Counter(
    "http_response_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
)

ACTIVE_CONNECTIONS = Gauge("active_connections", "Current number of active connections", ["app"])

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.1, 0.3, 0.5, 1.0, 2.0, 5.0],
)


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")
async def register_user(
    request: Request,
    user: Annotated[UserCreate, Field(description="User create data")],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        user = await user_service.create_user(user=user)
        REQUEST_TOTAL.labels(method="POST", endpoint="/users/register", status_code="201").inc()
        return user
    except ConflictException as e:
        REQUEST_TOTAL.labels(method="POST", endpoint="/users/register", status_code=str(e.status_code)).inc()
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.post("/token", status_code=status.HTTP_200_OK)
@limiter.limit("10/hour")
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """
    Аутентифицирует пользователя и возвращает JWT с email, role и id.
    """
    try:
        user = await user_service.authenticate_user(form_data.username, form_data.password)

        access_token = create_access_token(data={"sub": user.email, "id": user.id})
        refresh_token = create_refresh_token(data={"sub": user.email, "id": user.id})
        REQUEST_TOTAL.labels(method="POST", endpoint="/users/token", status_code="200").inc()
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except NotFoundException as e:
        REQUEST_TOTAL.labels(method="POST", endpoint="/users/token", status_code=str(e.status_code)).inc()
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.post("/refresh_token", response_model=TokenGroup)
async def update_access_token(
    request: RefreshTokenRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        token_group = await user_service.refresh_access_token(refresh_token=request.refresh_token)
        REQUEST_TOTAL.labels(method="POST", endpoint="/users/refresh_token", status_code="200").inc()
        return token_group
    except NotFoundException as e:
        REQUEST_TOTAL.labels(
            method="POST",
            endpoint="/users/refresh_token",
            status_code=str(e.status_code),
        ).inc()
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.get("/me", response_model=User, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_me(
    request: Request,
    user_service: Annotated[UserService, Depends(get_user_service)],
    user_email: Annotated[str, Depends(get_email_current_user)],
):
    try:
        user = await user_service.get_user_by_email(user_email)
        REQUEST_TOTAL.labels(method="GET", endpoint="/users/me", status_code="200").inc()
        return user
    except NotFoundException as e:
        REQUEST_TOTAL.labels(method="GET", endpoint="/users/me", status_code=str(e.status_code)).inc()
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: Annotated[int, Path(ge=1)],
    user_email: Annotated[str, Depends(get_email_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        result = await user_service.delete_user(user_id=user_id, email=user_email)
        if result:
            REQUEST_TOTAL.labels(method="DELETE", endpoint=f"/users/{user_id}", status_code="200").inc()
            return {"success": "user deleted"}
        return {"failed": "user not deleted"}
    except NotFoundException as e:
        REQUEST_TOTAL.labels(
            method="DELETE",
            endpoint=f"/users/{user_id}",
            status_code=str(e.status_code),
        ).inc()
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
