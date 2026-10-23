from fastapi import Form
from pydantic import BaseModel, ConfigDict


class Todo(BaseModel):
    id: int | None = None
    item: str

    @classmethod
    def as_form(cls, item: str = Form(..., min_length=1, pattern=r"\S")) -> "Todo":
        return cls(item=item.strip())


class TodoItem(BaseModel):
    item: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"item": "Прочитать следующую главу учебника"}
        }
    )


class TodoItems(BaseModel):
    todos: list[TodoItem]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "todos": [
                    {"item": "Изучить модели ответов FastAPI"},
                    {"item": "Подготовить отчёт по практической работе"},
                ]
            }
        }
    )
