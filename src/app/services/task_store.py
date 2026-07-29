from src.app.schemas.voice import Task, TaskCreate, TaskReplace, TaskUpdate

tasks: list[Task] = []
_next_id = 1


def get_all() -> list[Task]:
    return list(tasks)


def _find_index(task_id: int) -> int | None:
    for index, task in enumerate(tasks):
        if task.id == task_id:
            return index
    return None


def get_by_id(task_id: int) -> Task | None:
    index = _find_index(task_id)
    if index is None:
        return None
    return tasks[index]


def create(payload: TaskCreate) -> Task:
    global _next_id
    task = Task(id=_next_id, title=payload.title, done=payload.done)
    _next_id += 1
    tasks.append(task)
    return task


def replace(task_id: int, payload: TaskReplace) -> Task | None:
    index = _find_index(task_id)
    if index is None:
        return None
    updated = Task(id=task_id, title=payload.title, done=payload.done)
    tasks[index] = updated
    return updated


def update(task_id: int, payload: TaskUpdate) -> Task | None:
    index = _find_index(task_id)
    if index is None:
        return None
    current = tasks[index]
    updated = Task(
        id=task_id,
        title=payload.title if payload.title is not None else current.title,
        done=payload.done if payload.done is not None else current.done,
    )
    tasks[index] = updated
    return updated


def delete(task_id: int) -> bool:
    index = _find_index(task_id)
    if index is None:
        return False
    tasks.pop(index)
    return True
