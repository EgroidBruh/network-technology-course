from datetime import datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

Phone = Annotated[str, Field(pattern=r"^\+[1-9][0-9]{7,14}$")]


class Role(StrEnum):
    SPECIALIST = "SPECIALIST"
    SHIFT_LEAD = "SHIFT_LEAD"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"


class EmployeeCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr
    position: str = Field(min_length=1, max_length=150)
    role: Role = Role.SPECIALIST
    work_phone: Phone
    mobile_phone: Phone

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return value.lower()

    @model_validator(mode="after")
    def distinct_phones(self):
        if self.work_phone == self.mobile_phone:
            raise ValueError("Рабочий и мобильный телефоны должны различаться")
        return self


class Employee(EmployeeCreate):
    id: UUID
    created_at: datetime


