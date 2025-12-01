from fastapi import FastAPI, HTTPException
from typing import List
from models import Todo

app = FastAPI()
todos: List[Todo] = []

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/todos", response_model=List[Todo])
def list_todos():
    return todos

@app.post("/todos", response_model=Todo)
def create_todo(todo: Todo):
    # in a real app you'd auto-generate ids or use a DB
    todos.append(todo)
    return todo

@app.put("/todos/{todo_id}", response_model=Todo)
def toggle_todo(todo_id: int):
    for t in todos:
        if t.id == todo_id:
            t.completed = not t.completed
            return t
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    global todos
    todos = [t for t in todos if t.id != todo_id]
    return {"status": "deleted"}

