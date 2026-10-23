from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from todo import todo_router


app = FastAPI(
    title="Список задач — шаблоны Jinja2"
)


@app.get("/")
async def welcome() -> RedirectResponse:
    return RedirectResponse(url="/todo")


app.include_router(todo_router)
