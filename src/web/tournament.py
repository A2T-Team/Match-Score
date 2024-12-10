from fastapi import APIRouter, Request, Depends, Query, Form
from fastapi.templating import Jinja2Templates
from typing import Literal
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from uuid import UUID

from src.core.auth import get_current_user
from src.api.deps import get_db
from src.crud import tournaments
from src.models.user import User, Role
from src.schemas.tournament import TournamentSchema, UpdateTournamentRequest
from src.common import custom_exceptions
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from pydantic_core._pydantic_core import ValidationError

tournament_router = APIRouter(prefix="/tournament")
templates = Jinja2Templates(directory="src/templates")


@tournament_router.get("/")
def list_tournaments(
    request: Request,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    sort: Literal["asc", "desc"] | None = Query(default=None),
    search: str | None = Query(default=None),
    db_session: Session = Depends(get_db),
):
    flash_message = request.cookies.get("flash_message")
    token = request.cookies.get("token")
    user = get_current_user(token, db_session)
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


@tournament_router.get("/{tournament_id}/detail")
def get_tournament_html(
    request: Request,
    tournament_id: UUID,
    db_session: Session = Depends(get_db),
):
    flash_message = request.cookies.get("flash_message")
    token = request.cookies.get("token")
    user = get_current_user(token, db_session)

    tournament = tournaments.get_tournament(db_session, tournament_id)
    if tournament is None:
        response = RedirectResponse(url="/", status_code=302)
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


@tournament_router.get("/{tournament_id}/delete")
def delete_tournament_html(
    request: Request,
    tournament_id: UUID,
    db_session: Session = Depends(get_db),
):
    token = request.cookies.get("token")
    user = get_current_user(token, db_session)

    if user is None:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="flash_message", value="User not authenticated")
        return response
    
    tournament = tournaments.get_tournament(db_session, tournament_id)
    
    if tournament is None:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="flash_message", value="Tournament not found")
        return response

    if not tournaments.can_update_tournament(user, tournament):
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="flash_message", value="User not authorized")
        return response

    tournaments.delete_tournament(db_session, tournament_id)
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="flash_message", value="Tournament deleted successfully")

    return response


@tournament_router.get("/create")
def create_tournament_html(
    request: Request,
    db_session: Session = Depends(get_db),
):
    flash_message = request.cookies.get("flash_message")
    token = request.cookies.get("token")
    user = get_current_user(token, db_session)

    if user is None:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="flash_message", value="User not authenticated")
        return response

    if user.role not in {Role.ADMIN, Role.DIRECTOR}:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="flash_message", value="User not authorized")
        return response

    response = templates.TemplateResponse(
        request=request,
        name="create_tournament.html",
        context={
            "title": "Create Tournament",
            "flash_message": flash_message,
        },
    )
    response.delete_cookie("flash_message")
    return response


@tournament_router.post("/submit_tournament")
def submit_tournament(
    request: Request,
    name: str = Form(...),
    format: str = Form(...),
    match_format: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    prize: str = Form(...),
    win_points: str = Form(...),
    draw_points: str = Form(...),
    session: Session = Depends(get_db),
):
    token = request.cookies.get("token")
    user = get_current_user(token, session)

    if user is None:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="flash_message", value="User not authenticated")
        return response

    if user.role not in {Role.ADMIN, Role.DIRECTOR}:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="flash_message", value="User not authorized")
        return response

    try:
        tournament = TournamentSchema(
            name=name,
            format=format.lower(),
            match_format=match_format.lower(),
            start_time=start_time.replace("-", "/").replace("T", " "),
            end_time=end_time.replace("-", "/").replace("T", " "),
            prize=prize,
            win_points=win_points,
            draw_points=draw_points,
        )
    except ValidationError as e:
        response = RedirectResponse(url="/tournament/create", status_code=302)
        response.set_cookie(key="flash_message", value=f"{e}")
        return response

    try:
        tournament = tournaments.create(
            tournament=tournament, current_user=user, db_session=session
        )

    except custom_exceptions.NotFound as e:
        response = RedirectResponse(url="/tournament/create", status_code=302)
        response.set_cookie(
            key="flash_message", value=f"{e.key} '{e.key_value}' not found."
        )
        return response

    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            if "tournaments_name_key" in str(e.orig):
                response = RedirectResponse(url="/tournament/create", status_code=302)
                response.set_cookie(
                    key="flash_message",
                    value=f"Tournament with name '{tournament.name}' already exists",
                )
                return response
            else:
                response = RedirectResponse(url="/tournament/create", status_code=302)
                response.set_cookie(
                    key="flash_message", value="An unexpected integrity error occurred"
                )
                return response
        response = RedirectResponse(url="/tournament/create", status_code=302)
        response.set_cookie(key="flash_message", value="Database error")
        return response

    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="flash_message", value="Tournament created successfully")
    return response


@tournament_router.get("/{tournament_id}/create_matches")
def tournament_create_matches_html(
    request: Request,
    tournament_id: UUID,
    db_session: Session = Depends(get_db),
):
    flash_message = request.cookies.get("flash_message")
    token = request.cookies.get("token")
    user = get_current_user(token, db_session)

    if user is None:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="flash_message", value="User not authenticated")
        return response
    
    tournament = tournaments.get_tournament(db_session, tournament_id)
    
    if tournament is None:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="flash_message", value="Tournament not found")
        return response

    if not tournaments.can_update_tournament(user, tournament):
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="flash_message", value="User not authorized")
        return response

    try:
        tournaments.create_matches(
            tournament_id=tournament_id, db_session=db_session, current_user=user
        )
    except (
        custom_exceptions.InvalidNumberOfPlayers,
        custom_exceptions.InvalidRequest,
    ) as e:
        response = RedirectResponse(
            url=f"/tournament/{tournament_id}/detail", status_code=302
        )
        response.set_cookie(key="flash_message", value=f"{e}")
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


@tournament_router.get("/{tournament_id}/delete/player/{player_id}/")
def delete_player_html(
    request: Request,
    tournament_id: UUID,
    player_id: UUID,
    db_session: Session = Depends(get_db),
):
    token = request.cookies.get("token")
    user = get_current_user(token, db_session)
    redirect_url = request.headers.get("Referer", "/")

    if user is None:
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="flash_message", value="User not authenticated")
        return response
    
    tournament = tournaments.get_tournament(db_session, tournament_id)
    
    if tournament is None:
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="flash_message", value="Tournament not found")
        return response
    
    if not tournaments.can_update_tournament(user, tournament):
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="flash_message", value="User not authorized")
        return response
    
    if tournaments.has_matches(tournament):
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="flash_message", value="Tournament already has matches. Not allowed to delete players")
        return response
    
    try:
        tournaments.remove_player(db_session, tournament_id, player_id)
    except custom_exceptions.NotFound as e:
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(
            key="flash_message", value=f"{e.key} '{e.key_value}' not found."
        )
        return response
    response = RedirectResponse(url=redirect_url, status_code=302)
    response.set_cookie(key="flash_message", value="Player deleted successfully")

    return response


@tournament_router.get("/{tournament_id}/update")
def update_tournament_html(
    request: Request,
    tournament_id: UUID,
    db_session: Session = Depends(get_db),
):
    flash_message = request.cookies.get("flash_message")
    token = request.cookies.get("token")
    user = get_current_user(token, db_session)
    redirect_url = request.headers.get("Referer", "/")

    if user is None:
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="flash_message", value="User not authenticated")
        return response
    
    tournament = tournaments.get_tournament(db_session, tournament_id)
    
    if tournament is None:
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="flash_message", value="Tournament not found")
        return response

    if not tournaments.can_update_tournament(user, tournament):
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="flash_message", value="User not authorized")
        return response

    response = templates.TemplateResponse(
        request=request,
        name="update_tournament.html",
        context={
            "title": "Update Tournament",
            "flash_message": flash_message,
            "tournament": tournament,
        },
    )
    response.delete_cookie("flash_message")
    return response


@tournament_router.post("/{tournament_id}/submit_update")
def submit_tournament_update(
    request: Request,
    tournament_id: UUID,
    name: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    prize: str = Form(...),
    session: Session = Depends(get_db),
):
    token = request.cookies.get("token")
    user = get_current_user(token, session)
    redirect_url = request.headers.get("Referer", "/")

    if user is None:
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="flash_message", value="User not authenticated")
        return response

    tournament = tournaments.get_tournament(session, tournament_id)
    
    if tournament is None:
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="flash_message", value="Tournament not found")
        return response
    
    if not tournaments.can_update_tournament(user, tournament):
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="flash_message", value="User not authorized")
        return response
    
    name = name if name else None
    start_time = start_time.replace("-", "/").replace("T", " ") if start_time else None
    end_time = end_time.replace("-", "/").replace("T", " ") if end_time else None
    prize = prize if prize else None
    try:
        update_tournament_data = UpdateTournamentRequest(
            name=name,
            start_time=start_time,
            end_time=end_time,
            prize=prize,
        )
    except ValidationError as e:
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="flash_message", value=f"{e}")
        return response

    try:
        tournaments.update_tournament(
            tournament_id=tournament_id, data=update_tournament_data, db_session=session
        )
    except custom_exceptions.InvalidRequest as e:
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="flash_message", value=f"{e}")
        return response

    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            if "tournaments_name_key" in str(e.orig):
                response = RedirectResponse(url=redirect_url, status_code=302)
                response.set_cookie(
                    key="flash_message",
                    value=f"Tournament with name '{name}' already exists",
                )
                return response
            else:
                response = RedirectResponse(url=redirect_url, status_code=302)
                response.set_cookie(
                    key="flash_message", value="An unexpected integrity error occurred"
                )
                return response
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="flash_message", value="Database error")
        return response

    response = RedirectResponse(url=f"/tournament/{tournament_id}/detail", status_code=302)
    response.set_cookie(key="flash_message", value="Tournament updated successfully")
    return response


@tournament_router.get("/{tournament_id}/add_participant")
def add_participant_in_tournament_html(
    request: Request,
    tournament_id: UUID,
    db_session: Session = Depends(get_db),
):
    flash_message = request.cookies.get("flash_message")
    token = request.cookies.get("token")
    user = get_current_user(token, db_session)
    redirect_url = request.headers.get("Referer", "/")

    if user is None:
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="flash_message", value="User not authenticated")
        return response

    tournament = tournaments.get_tournament(db_session, tournament_id)
    
    if tournament is None:
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="flash_message", value="Tournament not found")
        return response
    
    if not tournaments.can_update_tournament(user, tournament):
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(key="flash_message", value="User not authorized")
        return response
    
    players = tournaments.get_all_players(db_session)

    response = templates.TemplateResponse(
        request=request,
        name="add_participant_in_tournament.html",
        context={
            "title": "Add Participant",
            "flash_message": flash_message,
            "tournament": tournament,
            "players": players,
        },
    )
    response.delete_cookie("flash_message")
    return response