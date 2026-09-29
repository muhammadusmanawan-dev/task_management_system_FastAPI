# from fastapi import FastAPI, status, HTTPException, Depends
# from sqlmodel import (
#     Field as SQLField,
#     SQLModel,
#     select,
# )
# from typing import Annotated
# from contextlib import asynccontextmanager
# from uuid import UUID

# from sqlalchemy.orm import DeclarativeBase
# from sqlalchemy.ext.asyncio import (
#     AsyncSession,
#     async_sessionmaker,
#     create_async_engine,
# )

# from fastapi_users.db import (
#     SQLAlchemyBaseUserTableUUID,
#     SQLAlchemyUserDatabase,
# )

# from fastapi_users import (
#     BaseUserManager,
#     FastAPIUsers,
#     UUIDIDMixin,
#     schemas,
# )

# from fastapi_users.authentication import (
#     AuthenticationBackend,
#     BearerTransport,
#     JWTStrategy,
# )

# SECRET = "Randomly add ki hay abhi"

# class Base(DeclarativeBase):
#     pass

# class User(SQLAlchemyBaseUserTableUUID, Base):
#     pass

# class Task(SQLModel, table=True):
#     id: int | None = SQLField(
#         default=None,
#         primary_key=True
#     )

#     title: str

#     completed: bool = False

#     owner_id: UUID


# #TASK SCHEMAS
# class TaskCreate(SQLModel):
#     title:str
#     completed:bool =False
# class TaskPublic(SQLModel):
#     id: int
#     title: str
#     completed: bool
#     owner_id: UUID
# class TaskUpdate(SQLModel):
#     title:str | None=None
#     completed:bool | None=None

# class UserRead(schemas.BaseUser[UUID]):
#     pass
# class UserCreate(schemas.BaseUserCreate):
#     pass
# class UserUpdate(schemas.BaseUserUpdate):
#     pass


# #DATABASE CONFIG
# sqlite_file_name="database.db"
# sqlite_url=f"sqlite+aiosqlite:///{sqlite_file_name}"

# engine=create_async_engine(sqlite_url)


# #CREATE DATABASE TABLES 
# async def create_db_and_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(
#             Base.metadata.create_all
#         )
#         await conn.run_sync(
#             SQLModel.metadata.create_all
#         )

# #DEPENDENCY INJECTION (database session)
# async_session_maker = async_sessionmaker(
#     engine,
#     expire_on_commit=False
# )
# async def get_session():
#     async with async_session_maker() as session:
#         yield session
# SessionDep = Annotated[AsyncSession, Depends(get_session)]


# async def get_user_db(session:SessionDep):
#     yield SQLAlchemyUserDatabase(session,User)
    
# class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
#     reset_password_token_secret = SECRET
#     verification_token_secret = SECRET

# async def get_user_manager(user_db=Depends(get_user_db)):
#     yield UserManager(user_db)

# #Authentication COnfig
# bearer_transport = BearerTransport(tokenUrl="auth/login")

# def get_jwt_strategy():
#     return JWTStrategy(
#         secret=SECRET,
#         lifetime_seconds=3600
#     )
# auth_backend = AuthenticationBackend(
#     name="jwt",
#     transport=bearer_transport,
#     get_strategy=get_jwt_strategy,
# )
# fastapi_users = FastAPIUsers(
#     get_user_manager,
#     [auth_backend],
# )


# #LIFESPAN
# @asynccontextmanager
# async def lifespan(app:FastAPI):
#     await create_db_and_tables()
#     yield

# #APP INITIALIZATION
# app=FastAPI(lifespan=lifespan)


# app.include_router(
#     fastapi_users.get_auth_router(auth_backend),
#     prefix="/auth",
#     tags=["auth"],
# )
# app.include_router(
#     fastapi_users.get_register_router(
#         UserRead,
#         UserCreate,
#     ),
#     prefix="/auth",
#     tags=["auth"],
# )
# current_active_user = fastapi_users.current_user(
#     active=True
# )

# @app.get("/")
# def home():
#     return {"message":"Welcome to the homepage"}

# @app.post("/tasks", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
# async def create_task(session:SessionDep, task:TaskCreate, current_user=Depends(current_active_user)):
#     new_task = Task(
#         title=task.title,
#         completed=task.completed,
#         owner_id=current_user.id
#     )
#     session.add(new_task)
#     await session.commit()
#     await session.refresh(new_task)
#     return new_task

# @app.get("/tasks", response_model=list[TaskPublic])
# async def all_tasks(session: SessionDep, completed:bool|None=None, limit:int|None=None):
    
#     statement=select(Task)
#     if completed is not None:
#         statement=statement.where(
#             Task.completed==completed
#         )

#     if limit is not None:
#         statement=statement.limit(limit)

#     result=await session.execute(statement)
#     tasks=result.scalars().all()
#     return tasks
    
# @app.get(
#     "/tasks/{task_id}",
#     response_model=TaskPublic
# )
# async def single_task(
#     session: SessionDep,
#     task_id: int
# ):

#     task = await session.get(
#         Task,
#         task_id
#     )

#     if not task:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Task not found"
#         )

#     return task


# @app.patch(
#     "/tasks/{task_id}",
#     response_model=TaskPublic,
#     status_code=status.HTTP_200_OK
# )
# async def update_task(
#     session: SessionDep,
#     task_id: int,
#     task_update: TaskUpdate
# ):

#     task = await session.get(
#         Task,
#         task_id
#     )

#     if not task:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Task Not Found"
#         )

#     update_data = task_update.model_dump(
#         exclude_unset=True
#     )

#     task.sqlmodel_update(
#         update_data
#     )

#     session.add(task)

#     await session.commit()

#     await session.refresh(task)

#     return task
# @app.delete(
#     "/tasks/{task_id}"
# )
# async def delete_task(
#     session: SessionDep,
#     task_id: int
# ):

#     task = await session.get(
#         Task,
#         task_id
#     )

#     if not task:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Task not found"
#         )

#     await session.delete(task)

#     await session.commit()

#     return {
#         "ok": True
#     }
