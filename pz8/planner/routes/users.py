from fastapi import APIRouter, HTTPException, status

from planner.models.users import NewUser, UserSignIn

user_router = APIRouter(tags=["User"])
users: dict[str, NewUser] = {}


@user_router.post("/signup")
async def sign_new_user(data: NewUser) -> dict[str, str]:
    if data.email in users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with supplied email exists",
        )
    users[data.email] = data
    return {"message": "User successfully registered!"}


@user_router.post("/signin")
async def sign_user_in(data: UserSignIn) -> dict[str, str]:
    user = users.get(data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )
    if user.password != data.password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Wrong credentials passed"
        )
    return {"message": "User signed in successfully"}
