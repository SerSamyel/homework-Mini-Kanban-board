from fastapi import APIRouter, HTTPException, status

from ..models import Task, TaskCreateRequest, TaskUpdateRequest
from ..store import TaskNotFoundError, UnknownColumnError, store

router = APIRouter(tags=["tasks"])


@router.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"description": "Validation error"}},
)
def create_task(payload: TaskCreateRequest) -> Task:
    """Append a new task to the end of its column. No auth — public."""
    try:
        task = store.create_task(
            title=payload.title,
            description=payload.description,
            column_id=payload.column_id,
        )
    except UnknownColumnError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return Task(**task)


@router.get(
    "/tasks/{id}",
    response_model=Task,
    responses={404: {"description": "Task not found"}},
)
def get_task(id: int) -> Task:
    """No auth — public."""
    try:
        task = store.get_task(id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Task(**task)


@router.patch(
    "/tasks/{id}",
    response_model=Task,
    responses={404: {"description": "Task not found"}, 422: {"description": "Validation error"}},
)
def update_task(id: int, payload: TaskUpdateRequest) -> Task:
    """Partial update — also used to move a task between columns/positions.

    No auth — public.
    """
    changes = payload.model_dump(exclude_unset=True)
    try:
        task = store.update_task(id, **changes)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UnknownColumnError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return Task(**task)


@router.delete(
    "/tasks/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Task not found"}},
)
def delete_task(id: int) -> None:
    """No auth — public."""
    try:
        store.delete_task(id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
