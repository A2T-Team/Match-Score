from fastapi import APIRouter, Depends, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.models.user import User
from src.schemas.user import CreateUserRequest, LoginRequest, UpdateEmailRequest
from src.crud.users import (get_all_users, create_user, login_user, get_me, update_email, get_by_username)

users_router = APIRouter(prefix="/users", tags=["users"])
templates = Jinja2Templates(directory="src/templates")


@users_router.post("/register")
def register_user(request: Request, user: CreateUserRequest, db: Session = Depends(get_db)):
    create_user(db, user)
    return templates.TemplateResponse("register_user.html", {"request": request, "message": "User registered successfully!"})


@users_router.post("/login")
def login_user_view(request: Request, user: LoginRequest, db: Session = Depends(get_db)):
    token = login_user(db, user)
    return templates.TemplateResponse("login_user.html", {"request": request, "message": "Login successful!", "token": token})


@users_router.get("/")
def view_users(request: Request, db: Session = Depends(get_db),
               username: str = Query(None), limit: int = Query(10)):
    if username:
        users = [get_by_username(db, username)]
    else:
        users = get_all_users(db, limit=limit)
    return templates.TemplateResponse("view_users.html", {"request": request, "users": users})


@users_router.get("/me")
def user_profile(request: Request, current_user: User = Depends(get_me)):
    return templates.TemplateResponse("user_profile.html", {"request": request, "user": current_user})


@users_router.post("/me/email")
def update_email_view(request: Request, new: UpdateEmailRequest,
                      db: Session = Depends(get_db), current_user: User = Depends(get_me)):
    updated_user = update_email(db, new, current_user)
    return templates.TemplateResponse("user_profile.html", {"request": request, "user": updated_user, "message": "Email updated successfully!"})
