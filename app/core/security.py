from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from fastapi_users import FastAPIUsers

from app.core.config import SECRET

from app.users.service import get_user_manager


bearer_transport = BearerTransport(
    tokenUrl="auth/login"
)

def get_jwt_strategy():
    return JWTStrategy(
        secret=SECRET,
        lifetime_seconds=3600
    )

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
