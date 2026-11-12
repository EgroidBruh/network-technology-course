from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from planner.database.connection import conn, make_engine
from planner.routes.events import event_router
from planner.routes.users import user_router


async def index() -> RedirectResponse:
    return RedirectResponse("/docs")


def create_app(database_url: str | None = None) -> FastAPI:
    engine = make_engine(database_url)

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        conn(engine)
        try:
            yield
        finally:
            engine.dispose()

    application = FastAPI(
        title="Планировщик событий — SQLite", version="2.0.0", lifespan=lifespan,
    )
    application.state.engine = engine
    application.include_router(user_router, prefix="/user")
    application.include_router(event_router, prefix="/event")
    application.add_api_route("/", index, include_in_schema=False)
    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("planner.main:app", host="0.0.0.0", port=8080, reload=True)
