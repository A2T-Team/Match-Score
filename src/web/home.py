from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from src.core.auth import get_current_user

index_router = APIRouter(prefix="")
templates = Jinja2Templates(directory="src/templates")


@index_router.get("/")
def index(request: Request):
    messages = []
    token = request.cookies.get("token")
    user = get_current_user(token)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Tournaments",
            "user": user,
            "messages": messages,
        },
    )
