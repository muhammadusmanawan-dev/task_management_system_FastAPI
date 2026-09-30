from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True
    )
    title: str
    completed: bool = False
    owner_id: UUID
