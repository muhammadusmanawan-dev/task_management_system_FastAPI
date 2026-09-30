from fastapi import APIRouter, Depends
from app.users.schemas import UserRead, UserCreate
from app.users.models import User
from app.core.security import (
    fastapi_users,
    auth_backend,
    current_active_user,
)


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

@router.get("/me")
async def get_me(
    current_user: User = Depends(current_active_user)
):
    return current_user
