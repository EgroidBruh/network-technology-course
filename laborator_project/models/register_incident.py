from datetime import datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Severity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class IncidentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    source: str = Field(min_length=1, max_length=100)
    error_code: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=5000)
    severity: Severity


class Incident(IncidentCreate):
    id: UUID
    status: Literal["OPEN"] = "OPEN"
    created_at: datetime


class IncidentCreatedEvent(BaseModel):
    id: UUID
    event_type: Literal["IncidentCreatedEvent"] = "IncidentCreatedEvent"
    incident_id: UUID
    severity: Severity
    occurred_at: datetime
