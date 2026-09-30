from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import fastapi_users


SessionDep = Annotated[
    AsyncSession,
    Depends(get_session)
]
current_active_user = fastapi_users.current_user(
    active=True
)
