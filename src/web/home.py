from fastapi import APIRouter, Request, Depends, Query, Form
from fastapi.templating import Jinja2Templates
from typing import Literal
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from src.api.deps import get_db
from src.crud import tournaments
from src.core import auth

index_router = APIRouter(prefix="")
templates = Jinja2Templates(directory="src/templates")


@index_router.get("/")
def index():
    return RedirectResponse(url="/tournament", status_code=302)


@index_router.post("/submit_login")
def submit_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_db),
):

    user = auth.authenticate_user(username, password, session)

    if not user:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="flash_message", value="Invalid username or password")
        return response

    else:
        access_token = auth.create_access_token(user=user)
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie("token", access_token)
        return response


@index_router.get("/login")
def login_page(request: Request, db_session: Session = Depends(get_db)):

    flash_message = request.cookies.get("flash_message")
    token = request.cookies.get("token")
    user = auth.get_current_user(token, db_session)

    if user:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="flash_message", value="Already logged in")
        return response

    response = templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "title": "Login",
            "flash_message": flash_message,
        },
    )
    response.delete_cookie("flash_message")
    return response

@index_router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("token")
    return response
