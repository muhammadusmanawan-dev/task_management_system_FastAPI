from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import create_db_and_tables
from app.users.router import router as users_router
from app.tasks.router import router as tasks_router
from fastapi import Request

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url.path}")

    response = await call_next(request)

    print(f"Response: {response.status_code}")

    return response

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
