from fastapi import FastAPI
from todo import todo_router


app = FastAPI(
    title="Практическая работа №4"
)


@app.get("/")
async def welcome() -> dict:
    return {
        "message": "Добро пожаловать в приложение Егора!"
    }


app.include_router(todo_router)
