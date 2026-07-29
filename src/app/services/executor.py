from typing import Any

from fastapi import HTTPException, status

from src.app.schemas.voice import InstructionPayload, TaskCreate, TaskReplace, TaskUpdate
from src.app.services import task_store


def execute_instruction(instruction: InstructionPayload) -> Any:
    """Run the routed task action. Used by /transcribe only (not by /instruction)."""
    method = instruction.method.upper().strip()
    endpoint = (instruction.endpoint or "").strip().rstrip("/") or "/"
    params = dict(instruction.params or {})

    if method == "GET" and endpoint == "/tasks":
        return [task.model_dump() for task in task_store.get_all()]

    if method == "POST" and endpoint == "/tasks":
        title = params.get("title")
        if not isinstance(title, str) or not title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="POST /tasks requires params.title",
            )
        done = _coerce_bool(params.get("done", False), field_name="done")
        task = task_store.create(TaskCreate(title=title.strip(), done=done))
        return task.model_dump()

    task_id = _resolve_task_id(endpoint, params)
    if task_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported instruction route: {method} {instruction.endpoint}. "
                "Expected /tasks or /tasks/{id}."
            ),
        )

    if method == "PUT":
        title = params.get("title")
        if not isinstance(title, str) or not title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PUT /tasks/{id} requires params.title",
            )
        if "done" not in params:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PUT /tasks/{id} requires params.done",
            )
        done = _coerce_bool(params.get("done"), field_name="done")
        task = task_store.replace(task_id, TaskReplace(title=title.strip(), done=done))
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )
        return task.model_dump()

    if method == "PATCH":
        patch_kwargs: dict[str, Any] = {}
        if "title" in params and params["title"] is not None:
            title = params["title"]
            if not isinstance(title, str) or not title.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="params.title must be a non-empty string when provided",
                )
            patch_kwargs["title"] = title.strip()
        if "done" in params and params["done"] is not None:
            patch_kwargs["done"] = _coerce_bool(params["done"], field_name="done")
        task = task_store.update(task_id, TaskUpdate(**patch_kwargs))
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


def _resolve_task_id(endpoint: str, params: dict[str, Any]) -> int | None:
    path_id = _extract_task_id_from_path(endpoint)
    if path_id is not None:
        return path_id
    for key in ("task_id", "id"):
        if key in params:
            try:
                return int(params[key])
            except (TypeError, ValueError):
                continue
    return None


def _extract_task_id_from_path(endpoint: str) -> int | None:
    parts = [part for part in endpoint.split("/") if part]
    if len(parts) != 2 or parts[0] != "tasks":
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def _coerce_bool(value: Any, *, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no"}:
            return False
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"params.{field_name} must be a boolean",
    )
