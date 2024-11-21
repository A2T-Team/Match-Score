from fastapi import APIRouter, Depends, Header
from typing import Annotated
from sqlalchemy.orm import Session
from typing import List
from src.core.authentication import get_current_user
from src.api.deps import get_db
from src.schemas.user import CreateUserRequest, UpdateUserRequest, LoginRequest
from src.models.user import User
from src.crud.users import get_all_users, create_user, get_user_by_id, login_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# @router.get("/")
# def read_users(token: Annotated[str, Header()], db: Session = Depends(get_db)):
#     user = get_current_user(token)
#     return get_all_users(db, user.id)

@router.get("/")
def read_users(db: Session = Depends(get_db)):
    return get_all_users(db)


@router.post("/register")
def create_user(user: CreateUserRequest, db: Session = Depends(get_db)):
    return create_user(db, user)


@router.get("/login")
def login_user(user: LoginRequest, db: Session = Depends(get_db)):
    return login_user(db, user)


@router.get("/me")
def read_user_me(token: Annotated[str, Header()], db: Session = Depends(get_db)):
    user = get_current_user(token)
    return user


@router.get("/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()


@router.put("/{user_id}")
def update_user(user_id: int, user: UpdateUserRequest, db: Session = Depends(get_db)):
    return user
