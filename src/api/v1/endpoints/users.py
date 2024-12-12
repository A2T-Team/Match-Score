from fastapi import APIRouter, Depends, Header, Query
from pydantic import EmailStr
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.common.custom_responses import BadRequest
from typing import Optional
import logging

from src.core.auth import get_current_user

from src.models.user import User, Role
from src.schemas.user import (CreateUserRequest, UpdateUserRequest, LoginRequest,
                              UpdateEmailRequest)

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
def view_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
               limit: int = Query(10, description="Limit the number of users to return"),
               username: Optional[str] = Query(None, min_length=3, max_length=50,
                                               description="Search user by username"),
               email: Optional[EmailStr] = Query(None, description="Search user by email")):
    if username and email:
        return BadRequest("Provide only one search parameter")
    if username:
        return get_by_username(db, username, current_user)
    if email:
        return get_by_email(db, email, current_user)
    return get_all_users(db, current_user, limit)


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return get_me(current_user)


@router.put("/me/email")
def update_my_email(new: UpdateEmailRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_credentials = update_email(db, new, current_user)
    return new_credentials


@router.put("/")
def update_user_credentials(new: UpdateUserRequest, db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            username: str = Query(None, min_length=3, max_length=50,
                            description="Update user by username"),
                            new_role: Optional[Role] = Query(None, description="Update user role")):
    new_credentials = update_user(db, new, username, current_user, new_role)
    return new_credentials


@router.delete("/")
def delete_user_by_username(db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
                            username: str = Query(None, min_length=3, max_length=50,
                            description="Delete user by username")):
    return delete_user(db, username, current_user)
