from uuid import UUID
from fastapi_users import BaseUserManager, UUIDIDMixin
from app.users.models import User
from app.core.config import settings
from fastapi import Depends
from app.users.repository import get_user_db

class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    reset_password_token_secret = settings.SECRET
    verification_token_secret = settings.SECRET

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
