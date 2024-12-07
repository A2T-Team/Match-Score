from fastapi import APIRouter, Request, Depends, Query
from fastapi.templating import Jinja2Templates
from typing import Literal
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from uuid import UUID

from src.core.auth import get_current_user
from src.api.deps import get_db
from src.crud import tournaments

tournament_router = APIRouter(prefix="/tournament")
templates = Jinja2Templates(directory="src/templates")


@tournament_router.get("/{tournament_id}")
def tournament(
    request: Request,
    tournament_id: UUID,
    db_session: Session = Depends(get_db),
):
    flash_message = request.cookies.get("flash_message")
    token = request.cookies.get("token")
    user = get_current_user(token)

    tournament = tournaments.get_tournament(db_session, tournament_id)
    if tournament is None:
        response = RedirectResponse(
            url="/",
            status_code=302
        )
        response.set_cookie(key="flash_message", value="Tournament not found")
        return response

    response = templates.TemplateResponse(
        request=request,
        name="tournament.html",
        context={
            "title": "Tournaments",
            "user": user,
            "flash_message": flash_message,
            "tournament": tournament,
        },
    )
    response.delete_cookie("flash_message")
    return response
