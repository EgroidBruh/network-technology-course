from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from planner.routes.events import event_router
from planner.routes.users import user_router

app = FastAPI(title="Планировщик событий", version="1.0.0")
app.include_router(user_router, prefix="/user")
app.include_router(event_router, prefix="/event")


@app.get("/", include_in_schema=False)
async def index() -> RedirectResponse:
    return RedirectResponse("/docs")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("planner.main:app", host="0.0.0.0", port=8080, reload=True)
