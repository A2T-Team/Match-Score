from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from src.api.deps import get_db
import logging

from src.core.auth import get_current_user

from src.models.user import User
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
def view_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_all_users(db, current_user)


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return get_me(current_user)


@router.get("/{username}")
def search_user_by_username(username: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_by_username(db, username, current_user)
    return user


@router.get("/{email}")
def search_user_by_email(email: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_by_email(db, email, current_user)
    return user


@router.put("/me/email/update")
def update_my_email(new: UpdateEmailRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_credentials = update_email(db, new, current_user)
    return new_credentials


@router.put("/{username}/update")
def update_user_credentials(username: str, new: UpdateUserRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_credentials = update_user(db, new, username, current_user)
    return new_credentials


@router.delete("/{username}/delete")
def delete_user_by_username(username: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return delete_user(db, username, current_user)
