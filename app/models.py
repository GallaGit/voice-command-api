from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    """Lo que envía el cliente en POST /tasks"""
    title: str = Field(..., min_length=1)
    done: bool = False


class Task(BaseModel):
    """Tarea completa: respuestas de GET, POST, PUT, PATCH"""
    id: int
    title: str
    done: bool