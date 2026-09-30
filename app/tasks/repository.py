from uuid import UUID

from sqlmodel import select

from app.tasks.models import Task


async def create_task(
    session,
    task: Task
):
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_tasks(
    session,
    user_id: UUID,
    completed: bool | None = None,
    limit: int | None = None
):
    statement = select(Task).where(
        Task.owner_id == user_id
    )

    if completed is not None:
        statement = statement.where(
            Task.completed == completed
        )

    if limit is not None:
        statement = statement.limit(limit)

    result = await session.execute(statement)
    return result.scalars().all()


async def get_task(
    session,
    task_id: UUID,
    user_id: UUID
):
    statement = select(Task).where(
        Task.id == task_id,
        Task.owner_id == user_id
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def update_task(
    session,
    task: Task,
    update_data: dict
):
    task.sqlmodel_update(update_data)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(
    session,
    task: Task
):
    await session.delete(task)
    await session.commit()
