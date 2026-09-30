from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import create_db_and_tables
from app.users.router import router as users_router
from app.tasks.router import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan
)


app.include_router(
    users_router
)

app.include_router(
    tasks_router
)


@app.get("/")
def home():
    return {
        "message": "Welcome to the homepage"
    }
