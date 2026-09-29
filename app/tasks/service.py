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
    completed=None,
    limit=None
):
    return await repository.get_tasks(
        session,
        completed,
        limit
    )

async def get_task(
    session,
    task_id: int
):
    return await repository.get_task(
        session,
        task_id
    )


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
