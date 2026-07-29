from typing import Any

from fastapi import HTTPException, status

from src.app.schemas.voice import InstructionPayload, TaskCreate, TaskReplace, TaskUpdate
from src.app.services import task_store


def execute_instruction(instruction: InstructionPayload) -> Any:
    method = instruction.method.upper()
    endpoint = instruction.endpoint.rstrip("/") or "/"
    params = instruction.params or {}

    if method == "GET" and endpoint == "/tasks":
        return [task.model_dump() for task in task_store.get_all()]

    if method == "POST" and endpoint == "/tasks":
        title = params.get("title")
        if not isinstance(title, str) or not title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="POST /tasks requires params.title",
            )
        done = params.get("done", False)
        if not isinstance(done, bool):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="params.done must be a boolean when provided",
            )
        task = task_store.create(TaskCreate(title=title.strip(), done=done))
        return task.model_dump()

    task_id = _extract_task_id(endpoint)
    if task_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported instruction route: {method} {instruction.endpoint}",
        )

    if method == "PUT":
        title = params.get("title")
        done = params.get("done")
        if not isinstance(title, str) or not title.strip() or not isinstance(done, bool):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PUT /tasks/{id} requires params.title and params.done",
            )
        task = task_store.replace(task_id, TaskReplace(title=title.strip(), done=done))
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )
        return task.model_dump()

    if method == "PATCH":
        title = params.get("title")
        done = params.get("done")
        if title is not None and (not isinstance(title, str) or not title.strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="params.title must be a non-empty string when provided",
            )
        if done is not None and not isinstance(done, bool):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="params.done must be a boolean when provided",
            )
        task = task_store.update(
            task_id,
            TaskUpdate(
                title=title.strip() if isinstance(title, str) else None,
                done=done if isinstance(done, bool) else None,
            ),
        )
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )
        return task.model_dump()

    if method == "DELETE":
        deleted = task_store.delete(task_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )
        return {"message": f"Task {task_id} deleted"}

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unsupported instruction route: {method} {instruction.endpoint}",
    )


def _extract_task_id(endpoint: str) -> int | None:
    parts = [part for part in endpoint.split("/") if part]
    if len(parts) != 2 or parts[0] != "tasks":
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None
