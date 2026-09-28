from fastapi import FastAPI, status, HTTPException, Depends
from sqlmodel import (
    Field as SQLField,
    SQLModel,
    create_engine,
    Session,
    Relationship,
    select,
)
from typing import Annotated
from contextlib import asynccontextmanager
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError


# ============================================================
# AUTHENTICATION CONFIGURATION
# ============================================================

ACCESS_TOKEN_EXPIRE_MINUTES = 30

SECRET_KEY = "your-secret-key"

ALGORITHM = "HS256"


# ============================================================
# JWT
# ============================================================

def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = (
            datetime.now(timezone.utc)
            + timedelta(minutes=15)
        )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# ============================================================
# OAUTH2
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)


# ============================================================
# PASSWORD HASHING
# ============================================================

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return password_hash.verify(
        plain_password,
        hashed_password
    )


# ============================================================
# DATABASE MODELS
# ============================================================

class User(SQLModel, table=True):

    id: int | None = SQLField(
        default=None,
        primary_key=True
    )

    username: str

    hashed_password: str

    tasks: list["Task"] = Relationship(
        back_populates="owner"
    )


class Task(SQLModel, table=True):

    id: int | None = SQLField(
        default=None,
        primary_key=True
    )

    title: str

    completed: bool = False

    owner_id: int = SQLField(
        foreign_key="user.id"
    )

    owner: User | None = Relationship(
        back_populates="tasks"
    )


# ============================================================
# API / VALIDATION MODELS
# ============================================================

class UserCreate(SQLModel):
    username: str
    password: str


class UserPublic(SQLModel):
    id: int
    username: str


class TaskCreate(SQLModel):
    title: str
    completed: bool = False


class TaskPublic(SQLModel):
    id: int
    title: str
    completed: bool
    owner_id: int


class TaskUpdate(SQLModel):
    title: str | None = None
    completed: bool | None = None


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

sqlite_file_name = "database.db"

sqlite_url = f"sqlite:///{sqlite_file_name}"


engine = create_engine(
    sqlite_url,
    connect_args={
        "check_same_thread": False
    }
)


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

def create_db_and_tables():

    SQLModel.metadata.create_all(
        engine
    )


# ============================================================
# DATABASE SESSION DEPENDENCY
# ============================================================

def get_session():

    with Session(engine) as session:
        yield session


SessionDep = Annotated[
    Session,
    Depends(get_session)
]


# ============================================================
# LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    create_db_and_tables()

    yield


# ============================================================
# APP INITIALIZATION
# ============================================================

app = FastAPI(
    lifespan=lifespan
)


# ============================================================
# AUTHENTICATION
# GET CURRENT USER
# ============================================================

def get_current_user(
    token: Annotated[
        str,
        Depends(oauth2_scheme)
    ],
    session: SessionDep
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (InvalidTokenError, ValueError, TypeError):

        raise credentials_exception

    user = session.get(
        User,
        user_id
    )

    if user is None:
        raise credentials_exception

    return user


# ============================================================
# CURRENT USER DEPENDENCY
# ============================================================

UserDep = Annotated[
    User,
    Depends(get_current_user)
]


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Welcome to the homepage"
    }


# ============================================================
# REGISTER USER
# ============================================================

@app.post(
    "/users",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    session: SessionDep,
    user: UserCreate
):

    # Check whether username already exists
    statement = select(User).where(
        User.username == user.username
    )

    existing_user = session.exec(
        statement
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Hash password
    hashed = hash_password(
        user.password
    )

    # Create database user
    new_user = User(
        username=user.username,
        hashed_password=hashed
    )

    session.add(new_user)

    session.commit()

    session.refresh(new_user)

    return new_user


# ============================================================
# GET ALL USERS
# ============================================================

@app.get(
    "/users",
    response_model=list[UserPublic],
    status_code=status.HTTP_200_OK
)
def get_users(
    session: SessionDep
):

    statement = select(User)

    users = session.exec(
        statement
    ).all()

    return users


# ============================================================
# LOGIN
# ============================================================

@app.post("/token")
def login(
    session: SessionDep,
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends()
    ]
):

    # Find user
    statement = select(User).where(
        User.username == form_data.username
    )

    user = session.exec(
        statement
    ).first()

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # Verify password
    password_is_correct = verify_password(
        form_data.password,
        user.hashed_password
    )

    if not password_is_correct:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # Create JWT
    access_token = create_access_token(
        data={
            "sub": str(user.id)
        },
        expires_delta=timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ============================================================
# CURRENT USER
# ============================================================

@app.get(
    "/users/me",
    response_model=UserPublic
)
def read_current_user(
    current_user: UserDep
):

    return current_user


# ============================================================
# PROTECTED TOKEN TEST
# ============================================================

@app.get("/protected")
def protected(
    token: Annotated[
        str,
        Depends(oauth2_scheme)
    ]
):

    return {
        "token": token
    }


# ============================================================
# CREATE TASK
# ============================================================

@app.post(
    "/tasks",
    response_model=TaskPublic,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    session: SessionDep,
    task: TaskCreate,
    current_user: UserDep
):

    # The owner comes from the logged-in user.
    # The client does NOT provide owner_id.

    new_task = Task(
        title=task.title,
        completed=task.completed,
        owner_id=current_user.id
    )

    session.add(new_task)

    session.commit()

    session.refresh(new_task)

    return new_task


# ============================================================
# GET MY TASKS
# ============================================================

@app.get(
    "/tasks",
    response_model=list[TaskPublic]
)
def all_tasks(
    session: SessionDep,
    current_user: UserDep,
    completed: bool | None = None,
    limit: int | None = None
):

    # Only get tasks belonging to current user
    statement = select(Task).where(
        Task.owner_id == current_user.id
    )

    # Optional completed filter
    if completed is not None:

        statement = statement.where(
            Task.completed == completed
        )

    # Optional limit
    if limit is not None:

        statement = statement.limit(limit)

    tasks = session.exec(
        statement
    ).all()

    return tasks


# ============================================================
# GET SINGLE TASK
# ============================================================

@app.get(
    "/tasks/{task_id}",
    response_model=TaskPublic
)
def single_task(
    session: SessionDep,
    task_id: int,
    current_user: UserDep
):

    task = session.get(
        Task,
        task_id
    )

    if not task:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Authorization check
    if task.owner_id != current_user.id:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task"
        )

    return task


# ============================================================
# UPDATE TASK
# ============================================================

@app.patch(
    "/tasks/{task_id}",
    response_model=TaskPublic,
    status_code=status.HTTP_200_OK
)
def update_task(
    session: SessionDep,
    task_id: int,
    task_update: TaskUpdate,
    current_user: UserDep
):

    task = session.get(
        Task,
        task_id
    )

    if not task:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Authorization check
    if task.owner_id != current_user.id:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this task"
        )

    # Only update fields sent by the client
    update_data = task_update.model_dump(
        exclude_unset=True
    )

    task.sqlmodel_update(
        update_data
    )

    session.add(task)

    session.commit()

    session.refresh(task)

    return task


# ============================================================
# DELETE TASK
# ============================================================

@app.delete(
    "/tasks/{task_id}"
)
def delete_task(
    session: SessionDep,
    task_id: int,
    current_user: UserDep
):

    task = session.get(
        Task,
        task_id
    )

    if not task:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Authorization check
    if task.owner_id != current_user.id:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this task"
        )

    session.delete(task)

    session.commit()

    return {
        "ok": True
    }
