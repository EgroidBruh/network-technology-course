from pydantic import ConfigDict, field_validator
from sqlmodel import Column, Field, JSON, SQLModel


class EventBase(SQLModel):
    title: str = Field(min_length=1)
    image: str
    description: str
    tags: list[str] = Field(sa_column=Column(JSON, nullable=False))
    location: str = Field(min_length=1)


class Event(EventBase, table=True):
    __tablename__ = "events"

    id: int | None = Field(default=None, primary_key=True)


class EventCreate(EventBase):
    # Optional explicit ID preserves compatibility with practical work 7.
    id: int | None = Field(default=None, gt=0)

    model_config = ConfigDict(extra="forbid", json_schema_extra={"example": {
        "title": "FastAPI Book Launch",
        "image": "https://example.com/book.png",
        "description": "Обсуждение книги FastAPI",
        "tags": ["python", "fastapi"],
        "location": "Google Meet",
    }})


class EventRead(EventBase):
    id: int


class EventUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1)
    image: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    location: str | None = Field(default=None, min_length=1)

    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "example": {"location": "Hybrid"}
    })

    @field_validator("*", mode="before")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("Omit unchanged fields instead of sending null")
        return value
