from uuid import UUID
from app.core.exceptions import TaskNotFoundException
from app.tasks.models import Task
from app.tasks import repository


async def create_task(
    session,
    task_data,
    current_user
):
    new_task = Task(
        title=task_data.title,
        completed=task_data.completed,
        owner_id=current_user.id
    )

    return await repository.create_task(
        session,
        new_task
    )

async def get_tasks(
    session,
    user_id: UUID,
    completed=None,
    limit=None
):
    return await repository.get_tasks(
        session,
        user_id,
        completed,
        limit
    )

async def get_task(
    session,
    task_id: UUID,
    user_id: UUID
):
    task=await repository.get_task(
        session,
        task_id,
        user_id
    )

    if task is None:
        raise TaskNotFoundException()

    return task

async def update_task(
    session,
    task,
    task_update
):
    update_data = task_update.model_dump(
        exclude_unset=True
    )

    return await repository.update_task(
        session,
        task,
        update_data
    )

async def delete_task(
    session,
    task
):
    await repository.delete_task(
        session,
        task
    )
