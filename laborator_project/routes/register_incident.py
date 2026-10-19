from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Request

from models.register_incident import Incident, IncidentCreate, IncidentCreatedEvent

router = APIRouter(prefix="/incidents", tags=["Сценарий 3: регистрация инцидента"])


@router.post("", response_model=Incident, status_code=201)
def register_incident(data: IncidentCreate, request: Request):
    now = datetime.now(timezone.utc)
    incident = Incident(id=uuid4(), created_at=now, **data.model_dump())
    event = IncidentCreatedEvent(
        id=uuid4(), incident_id=incident.id, severity=incident.severity, occurred_at=now,
    )
    request.app.state.incidents[incident.id] = incident
    # Событие пока только хранится в памяти; доставка и обзвон появятся позже.
    request.app.state.incident_events[incident.id] = [event]
    return incident


@router.get("", response_model=list[Incident])
def list_incidents(request: Request):
    return list(request.app.state.incidents.values())


@router.get("/{incident_id}", response_model=Incident)
def get_incident(incident_id: UUID, request: Request):
    incident = request.app.state.incidents.get(incident_id)
    if incident is None:
        raise HTTPException(404, "Инцидент не найден")
    return incident


@router.get("/{incident_id}/events", response_model=list[IncidentCreatedEvent])
def list_incident_events(incident_id: UUID, request: Request):
    if incident_id not in request.app.state.incidents:
        raise HTTPException(404, "Инцидент не найден")
    return request.app.state.incident_events[incident_id]
