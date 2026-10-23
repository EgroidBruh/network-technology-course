from pydantic import BaseModel, ConfigDict, EmailStr, Field

from planner.models.events import Event


class User(BaseModel):
    email: EmailStr
    events: list[Event] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "fastapi@packt.com", "events": []}
        }
    )


class NewUser(User):
    password: str = Field(min_length=1, repr=False)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "fastapi@packt.com",
                "password": "Stro0ng!",
                "events": [],
            }
        }
    )


class UserSignIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, repr=False)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "fastapi@packt.com", "password": "Stro0ng!"}
        }
    )
