from fastapi import APIRouter
from app.storage import tasks
from app.models import Task, TaskCreate
router = APIRouter()

@router.get("/tasks")
def get_tasks():
    return tasks

@router.post("/tasks", response_model=Task)
def create_task(payload: TaskCreate):
   
   ...