from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, delete, select

from planner.database.connection import get_session
from planner.models.events import Event, EventCreate, EventRead, EventUpdate

event_router = APIRouter(tags=["Events"])
SessionDep = Annotated[Session, Depends(get_session)]
EventId = Annotated[int, Path(gt=0)]


def find_event(session: Session, id: int) -> Event:
    event = session.get(Event, id)
    if event is None:
        raise HTTPException(404, "Event with supplied ID does not exist")
    return event


@event_router.get("/", response_model=list[EventRead])
def retrieve_all_events(session: SessionDep):
    return session.exec(select(Event).order_by(Event.id)).all()


@event_router.get("/{id}", response_model=EventRead)
def retrieve_event(id: EventId, session: SessionDep):
    return find_event(session, id)


@event_router.post("/new")
def create_event(body: EventCreate, session: SessionDep):
    event = Event.model_validate(body)
    session.add(event)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Event with supplied ID already exists") from None
    session.refresh(event)
    return {"message": "Event created successfully", "id": event.id}


@event_router.put("/edit/{id}", response_model=EventRead)
@event_router.put("/{id}", response_model=EventRead, include_in_schema=False)
def update_event(id: EventId, body: EventUpdate, session: SessionDep):
    event = find_event(session, id)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(event, key, value)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@event_router.delete("/delete/{id}")
@event_router.delete("/{id}", include_in_schema=False)
def delete_event(id: EventId, session: SessionDep):
    event = find_event(session, id)
    session.delete(event)
    session.commit()
    return {"message": "Event deleted successfully"}


@event_router.delete("/")
def delete_all_events(session: SessionDep):
    session.exec(delete(Event))
    session.commit()
    return {"message": "Events deleted successfully"}
