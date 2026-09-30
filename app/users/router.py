from fastapi import APIRouter

from app.core.security import fastapi_users, auth_backend
from app.users.schemas import UserRead, UserCreate


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

router.include_router(
    fastapi_users.get_auth_router(
        auth_backend
    )
)

router.include_router(
    fastapi_users.get_register_router(
        UserRead,
        UserCreate
    )
)
