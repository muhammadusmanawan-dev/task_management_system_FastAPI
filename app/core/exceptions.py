from fastapi import HTTPException, status


def task_not_found():
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )
