from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from planner.database.connection import get_session
from planner.models.users import NewUser, UserRecord, UserSignIn
from planner.security import hash_password, verify_password

user_router = APIRouter(tags=["User"])
SessionDep = Annotated[Session, Depends(get_session)]


@user_router.post("/signup")
def sign_new_user(data: NewUser, session: SessionDep) -> dict[str, str]:
    user = UserRecord(
        email=str(data.email), password_hash=hash_password(data.password),
        events=[event.model_dump() for event in data.events],
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "User with supplied email exists") from None
    return {"message": "User successfully registered!"}


@user_router.post("/signin")
def sign_user_in(data: UserSignIn, session: SessionDep) -> dict[str, str]:
    user = session.exec(select(UserRecord).where(UserRecord.email == str(data.email))).first()
    if user is None:
        raise HTTPException(404, "User does not exist")
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(403, "Wrong credentials passed")
    return {"message": "User signed in successfully"}
