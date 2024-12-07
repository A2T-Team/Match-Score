from fastapi import APIRouter, Request, Depends, Query
from fastapi.templating import Jinja2Templates
from typing import Literal
from sqlalchemy.orm import Session

from src.core.auth import get_current_user
from src.api.deps import get_db
from src.crud import tournaments

index_router = APIRouter(prefix="")
templates = Jinja2Templates(directory="src/templates")


@index_router.get("/")
def index(
    request: Request,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    sort: Literal["asc", "desc"] | None = Query(default=None),
    search: str | None = Query(default=None),
    db_session: Session = Depends(get_db),
):
    flash_message = request.cookies.get("flash_message")
    token = request.cookies.get("token")
    user = get_current_user(token)
    all_tournaments = tournaments.view_all_tournaments(
        db_session, offset=offset, limit=limit, sort=sort, search=search
    )

    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Tournaments",
            "user": user,
            "flash_message": flash_message,
            "tournaments": all_tournaments,
        },
    )
    response.delete_cookie("flash_message")
    return response


# @index_router.get("/tournament/{tournament_id}")
# def tournament(
#     request: Request,
#     tournament_id: str,
#     db_session: Session = Depends(get_db),
# ):
#     flash_message = request.cookies.get("flash_message")
#     token = request.cookies.get("token")
#     user = get_current_user(token)
#     all_tournaments = tournaments.view_all_tournaments(
#         db_session, offset=offset, limit=limit, sort=sort, search=search
#     )

#     response = templates.TemplateResponse(
#         request=request,
#         name="index.html",
#         context={
#             "title": "Tournaments",
#             "user": user,
#             "flash_message": flash_message,
#             "tournaments": all_tournaments,
#         },
#     )
#     response.delete_cookie("flash_message")
#     return response
