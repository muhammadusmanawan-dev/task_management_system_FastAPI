from uuid import UUID

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True
    )
    title: str
    completed: bool = False
    owner_id: UUID
