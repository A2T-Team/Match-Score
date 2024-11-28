from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from src.api.deps import get_db
import logging

from typing import Annotated

from src.schemas.user import CreateUserRequest, UpdateUserRequest, LoginRequest, UpdateEmailRequest

from src.crud.users import (get_all_users, create_user, login_user,
                            get_me, update_email,
                            update_user, get_by_username,
                            get_by_email, delete_user)


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register")
def register(user: CreateUserRequest, db: Session = Depends(get_db)):
    return create_user(db, user)


@router.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    token = login_user(db, user)
    return token


@router.get("/")
def view_users(token: Annotated[str, Header()], db: Session = Depends(get_db)):
    return get_all_users(db, token)


@router.get("/me")
def me(token: Annotated[str, Header()], db: Session = Depends(get_db)):
    user = get_me(db, token)
    return user


@router.get("/{username}")
def search_user_by_username(username: str, token: Annotated[str, Header()], db: Session = Depends(get_db)):
    user = get_by_username(db, username, token)
    return user


@router.get("/{email}")
def search_user_by_email(email: str, token: Annotated[str, Header()], db: Session = Depends(get_db)):
    user = get_by_email(db, email, token)
    return user


@router.put("/me/email/update")
def update_my_email(token: Annotated[str, Header()], new: UpdateEmailRequest, db: Session = Depends(get_db)):
    new_credentials = update_email(db, new, token)
    return new_credentials


@router.put("/{username}/update")
def update_user_credentials(token: Annotated[str, Header()], username: str, new: UpdateUserRequest, db: Session = Depends(get_db)):
    new_credentials = update_user(db, new, username, token)
    return new_credentials


@router.delete("/{username}/delete")
def delete_user_by_username(token: Annotated[str, Header()], username: str, db: Session = Depends(get_db)):
    return delete_user(db, username, token)
