"""SQLite engine, schema initialization and one session per request."""

import os
from pathlib import Path
from collections.abc import Iterator

from fastapi import Request
from sqlalchemy.engine import Engine, make_url
from sqlmodel import Session, SQLModel, create_engine


def make_engine(database_url: str | None = None) -> Engine:
    url = make_url(database_url or os.getenv("DATABASE_URL", "sqlite:///./data/planner.db"))
    if url.get_backend_name() != "sqlite":
        raise ValueError("DATABASE_URL must use SQLite")
    return create_engine(
        url, connect_args={"check_same_thread": False, "timeout": 30},
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    )


def conn(engine: Engine) -> None:
    # Register both tables before creating the schema.
    from planner.models.events import Event  # noqa: F401
    from planner.models.users import UserRecord  # noqa: F401

    filename = engine.url.database
    if filename and filename != ":memory:":
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)


def get_session(request: Request) -> Iterator[Session]:
    with Session(request.app.state.engine) as session:
        yield session
