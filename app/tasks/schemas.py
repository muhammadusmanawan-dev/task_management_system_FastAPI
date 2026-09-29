from sqlmodel import SQLModel
from uuid import UUID
class TaskCreate(SQLModel):
    title:str
    completed:bool =False
class TaskPublic(SQLModel):
    id: int
    title: str
    completed: bool
    owner_id: UUID
class TaskUpdate(SQLModel):
    title:str | None=None
    completed:bool | None=None
