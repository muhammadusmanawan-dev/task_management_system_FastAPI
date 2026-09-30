from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi import Depends
from app.core.database import get_session
from app.users.models import User

async def get_user_db(session=Depends(get_session)):
    yield SQLAlchemyUserDatabase(session,User)
