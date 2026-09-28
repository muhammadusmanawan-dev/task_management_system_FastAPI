from fastapi import FastAPI, Request, status, HTTPException, Depends
#from pydantic import Field
from sqlmodel import Field as SQLField, SQLModel, create_engine, Session, Relationship, select
from typing import Annotated
from contextlib import asynccontextmanager

#DATABASE MODELS
class User(SQLModel, table=True):
    id:int | None =SQLField(default=None, primary_key=True)
    username: str
    tasks:list["Task"] =Relationship(back_populates="owner")

class Task(SQLModel, table=True):
    id:int | None =SQLField(default=None, primary_key=True)
    title:str
    completed:bool =False
    owner_id: int =SQLField(foreign_key="user.id")
    owner: User|None =Relationship(back_populates="tasks")

#SQL Model Validations
class UserCreate(SQLModel):
    username: str
class UserPublic(SQLModel):
    id:int
    username:str

class TaskCreate(SQLModel):
    title:str
    completed:bool =False
    owner_id:int
class TaskPublic(SQLModel):
    id: int
    title: str
    completed: bool
    owner_id: int

class TaskUpdate(SQLModel):
    title:str | None=None
    completed:bool | None=None
    owner_id:int | None=None



#DATABASE CONFIG
sqlite_file_name="database.db"
sqlite_url=f"sqlite:///{sqlite_file_name}"

engine=create_engine(
    sqlite_url,
    connect_args={"check_same_thread":False}
)
#CREATE DATABASE TABLES 
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


#DEPENDENCY INJECTION (database session)
def get_session():
    with Session(engine) as session:
        yield session
SessionDep = Annotated[Session, Depends(get_session)]


#LIFESPAN
@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_tables()
    yield


#APP INITIALIZATION
app=FastAPI(lifespan=lifespan)

# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables
    

# tasks = [
#     {
#         "id": 1,
#         "title": "learn FastAPI",
#         "completed": False,
#         "owner": {"id": 101, "username": "john_doe"},
#     },
#     {
#         "id": 2,
#         "title": "Build Task API",
#         "completed": False,
#         "owner": {"id": 102, "username": "jane_smith"},
#     },
#     {
#         "id": 3,
#         "title": "Practice FastAPI",
#         "completed": True,
#         "owner": {"id": 101, "username": "john_doe"},
#     },
#     {
#         "id": 4,
#         "title": "Practice FastAPI",
#         "completed": True,
#         "owner": {"id": 103, "username": "alex_dev"},
#     },
# ]

@app.get("/")
def home():
    return {"message":"Welcome to the homepage"}

@app.post("/users", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(session:SessionDep, user:UserCreate):
    new_user=User.model_validate(user)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@app.get("/users", response_model=list[UserPublic], status_code=status.HTTP_200_OK)
def get_users(session:SessionDep):
    statement=select(User)
    users=session.exec(statement).all()
    return users



@app.post("/tasks", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
def create_task(session:SessionDep, task:TaskCreate):
    new_task=Task.model_validate(task)
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task

@app.get("/tasks", response_model=list[TaskPublic])
def all_tasks(session: SessionDep, completed:bool|None=None, limit:int|None=None):
    
    statement=select(Task)
    if completed is not None:
        statement=statement.where(
            Task.completed==completed
        )

    if limit is not None:
        statement=statement.limit(limit)

    tasks=session.exec(statement).all()
    return tasks
    
@app.get("/tasks/{task_id}", response_model=TaskPublic)
def single_task(session:SessionDep, task_id:int):
    task=session.get(Task,task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task

@app.patch("/tasks/{task_id}", response_model=TaskPublic,status_code=status.HTTP_200_OK)
def update_task(session:SessionDep, task_id:int, task_update:TaskUpdate):
    task=session.get(Task,task_id)

    if not task:    
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task Not Found"
        )
    update_data=task_update.model_dump(exclude_unset=True)
    task.sqlmodel_update(update_data)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# def get_db():
#     db=create_database_session()
#     try:
#         yield db
#     finally:
#         db.close()

# def get_current_user():
#     return{"Message": "Hi"}


# @app.get("/tasks/db")
# def tasks_db():
    # db=create_database_session()
    # tasks=db.query()
    # db.close
    # return tasks

# @app.get("/tasks")
# def get_tasks(user=Depends(get_current_user)):
#     return user

@app.delete("/tasks/{task_id}")
def delete_task(session: SessionDep, task_id: int):

    task = session.get(Task,task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    session.delete(task)
    session.commit()

    return {"ok": True}
