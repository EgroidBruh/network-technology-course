from fastapi import APIRouter, HTTPException, Path, status
from model import Todo, TodoItem, TodoItems


todo_router = APIRouter()

todo_list: list[Todo] = []

NOT_FOUND = "Егор, задача с указанным ID не найдена."


@todo_router.post("/todo", status_code=status.HTTP_201_CREATED)
async def add_todo(todo: Todo) -> dict:
    if any(existing.id == todo.id for existing in todo_list):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Егор, задача с указанным ID уже существует.",
        )
    todo_list.append(todo)

    return {
        "message": "Егор, задача успешно добавлена!"
    }


@todo_router.get("/todo", response_model=TodoItems)
async def retrieve_todos() -> dict:
    return {
        "todos": todo_list
    }


@todo_router.get("/todo/{todo_id}")
async def get_single_todo(
    todo_id: int = Path(..., title="ID задачи")
) -> dict:

    for todo in todo_list:
        if todo.id == todo_id:
            return {"todo": todo}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)


@todo_router.put("/todo/{todo_id}")
async def update_todo(
    todo_data: TodoItem,
    todo_id: int = Path(..., title="ID задачи для обновления"),
) -> dict:
    for todo in todo_list:
        if todo.id == todo_id:
            todo.item = todo_data.item
            return {"message": "Егор, задача успешно обновлена!"}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)


@todo_router.delete("/todo/{todo_id}")
async def delete_single_todo(
    todo_id: int = Path(..., title="ID задачи для удаления"),
) -> dict:
    for index, todo in enumerate(todo_list):
        if todo.id == todo_id:
            todo_list.pop(index)
            return {"message": "Егор, задача успешно удалена!"}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)


@todo_router.delete("/todo")
async def delete_all_todo() -> dict:
    todo_list.clear()
    return {"message": "Егор, все задачи успешно удалены!"}
