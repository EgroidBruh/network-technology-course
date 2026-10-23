from pydantic import BaseModel, ConfigDict, Field


class Event(BaseModel):
    id: int = Field(gt=0)
    title: str = Field(min_length=1)
    image: str
    description: str
    tags: list[str]
    location: str = Field(min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "FastAPI Book Launch",
                "image": "https://linktomyimage.com/image.png",
                "description": "Обсуждение книги и примеров приложений FastAPI.",
                "tags": ["python", "fastapi", "book", "launch"],
                "location": "Google Meet",
            }
        }
    )
