from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.common.dependencies import (
    SessionDep,
    current_active_user,
)

from app.tasks.schemas import (
    TaskCreate,
    TaskPublic,
    TaskUpdate,
)

from app.tasks import service


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@router.post("",response_model=TaskPublic,
    status_code=status.HTTP_201_CREATED
)
async def create_task(
    session: SessionDep,
    task: TaskCreate,
    current_user=Depends(current_active_user)
):
    return await service.create_task(
        session,
        task,
        current_user
    )


@router.get("",response_model=list[TaskPublic])
async def all_tasks(
    session: SessionDep,
    completed: bool | None = None,
    limit: int | None = None
):
    return await service.get_tasks(
        session,
        completed,
        limit
    )


@router.get("/{task_id}", response_model=TaskPublic
)
async def single_task(
    session: SessionDep,
    task_id: int
):
    task = await service.get_task(
        session,
        task_id
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.patch("/{task_id}",response_model=TaskPublic,status_code=status.HTTP_200_OK)
async def update_task(
    session: SessionDep,
    task_id: int,
    task_update: TaskUpdate
):
    task = await service.get_task(
        session,
        task_id
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return await service.update_task(
        session,
        task,
        task_update
    )


@router.delete("/{task_id}")
async def delete_task(
    session: SessionDep,
    task_id: int
):
    task = await service.get_task(
        session,
        task_id
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    await service.delete_task(
        session,
        task
    )

    return {
        "ok": True
    }
