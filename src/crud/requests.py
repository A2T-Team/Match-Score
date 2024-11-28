from sqlalchemy.orm import Session
from typing import List
import logging
import uuid
import re

from src.common.custom_responses import NotFound, BadRequest, ForbiddenAccess
from src.core.authentication import get_current_user

from src.models.request import RequestType
from src.models.request import Requests
from src.models.user import User, Role
from src.models.player import Player

from src.schemas.request import CreateRequest, RequestResponse

from src.crud.users import get_id_by_username, is_admin
from src.crud.players import update_player_with_user


logger = logging.getLogger(__name__)


def creating_request(db: Session, request: CreateRequest, token: str) -> RequestResponse | NotFound | BadRequest:

    """
    Create a new request in the database.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        request (CreateRequest): Contains the details of the request.
        token (str): The token of the user making the request.

    Returns:
        RequestResponse: The details of the created request.
    """

    user_id = get_id_by_username(db, get_current_user(token))

    db_request = Requests(
        user_id=user_id,
        request_type=request.request_type,
        request_reason=request.request_reason
    )

    user = db.query(User).filter(User.id == user_id).first()

    if db_request.request_type == RequestType.PROMOTE and user.role == Role.DIRECTOR:
        return BadRequest("You are already a director")

    if db_request.request_type == RequestType.DEMOTE and user.role == Role.USER:
        return BadRequest("There is no role to demote to")

    if db_request.request_type == RequestType.LINK:
        potential_player = db.query(Player).filter(Player.user_id == user_id).first()
        if potential_player:
            return BadRequest("You are already linked to a player")
        if not re.match(r"[a-zA-Z]+\s[a-zA-Z]+", request.request_reason):
            return BadRequest("Invalid player name format")

    if db_request.request_type == RequestType.UNLINK:
        player = db.query(Player).filter(Player.user_id == user_id).first()
        if not player:
            return BadRequest("You are not linked to any player")

    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    return RequestResponse(request_id=db_request.id, created_at=db_request.created_at,
                           request_type=db_request.request_type, user_id=db_request.user_id,
                           request_reason=db_request.request_reason)


def view_requests(db: Session, token: str) -> (List[RequestResponse] | NotFound | ForbiddenAccess):

    """
    Retrieve all requests from the database.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        token (str): The token of the user making the request.

    Returns:
        List[RequestResponse]: A list of all requests in the database.
    """

    user_id = get_id_by_username(db, get_current_user(token))

    if not is_admin(db, user_id):
        return ForbiddenAccess()

    if not db.query(Requests).all():
        return NotFound(key="Requests", key_value="")

    requests = db.query(Requests).all()

    return [RequestResponse(request_id=request.id, created_at=request.created_at, request_type=request.request_type,
                            user_id=request.user_id, request_reason=request.request_reason) for request in requests]


def open_request(db: Session, request_id: uuid.UUID, token: str) -> (RequestResponse | NotFound | ForbiddenAccess):

    """
    Retrieve a request from the database by its ID.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        request_id (uuid.UUID): The ID of the request to retrieve.
        token (str): The token of the user making the request.

    Returns:
        RequestResponse: The details of the requested request.
    """

    user_id = get_id_by_username(db, get_current_user(token))

    if not is_admin(db, user_id):
        return ForbiddenAccess()

    request = db.query(Requests).filter(Requests.id == request_id).first()

    if not request:
        return NotFound(key="Request ID", key_value=str(request_id))

    return RequestResponse(request_id=request.id, created_at=request.created_at, request_type=request.request_type,
                           user_id=request.user_id, request_reason=request.request_reason)


def accept_request(db: Session, request_id: uuid.UUID, token: str) -> (str | NotFound | BadRequest | ForbiddenAccess):

    """
    Accept a request in the database.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        request_id (uuid.UUID): The ID of the request to accept.
        token (str): The token of the user making the request.

    Returns:
        str: A message indicating the request was successfully accepted.
    """

    user_id = get_id_by_username(db, get_current_user(token))

    if not is_admin(db, user_id):
        return ForbiddenAccess()

    request = db.query(Requests).filter(Requests.id == request_id).first()

    if not request:
        return NotFound(key="Request ID", key_value=str(request_id))

    user = db.query(User).filter(User.id == request.user_id).first()

    if request.request_type == RequestType.PROMOTE:
        user.role = Role.DIRECTOR

    if request.request_type == RequestType.DEMOTE:
        user.role = Role.USER

    if request.request_type == RequestType.DELETE:
        db.delete(user)

    if request.request_type == RequestType.LINK:

        firstname, lastname = request.request_reason.split(" ")
        player = db.query(Player).filter(Player.first_name == firstname, Player.last_name == lastname).first()

        if not player:
            db.delete(request)
            db.commit()
            return NotFound(key="Player", key_value=request.request_reason)

        update_player_with_user(db, player.id, request.user_id)

    if request.request_type == RequestType.UNLINK:
        player = db.query(Player).filter(Player.user_id==request.user_id).first()
        player.user_id = None

    db.delete(request)
    db.commit()

    return "Request accepted"


def reject_request(db: Session, request_id: uuid.UUID, token: str) -> (str | NotFound | ForbiddenAccess):

    """
    Reject a request in the database.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        request_id (uuid.UUID): The ID of the request to reject.
        token (str): The token of the user making the request.

    Returns:
        str: A message indicating the request was successfully rejected.
    """

    user_id = get_id_by_username(db, get_current_user(token))

    if not is_admin(db, user_id):
        return ForbiddenAccess()

    request = db.query(Requests).filter(Requests.id == request_id).first()

    if not request:
        return NotFound(key="Request ID", key_value=str(request_id))

    db.delete(request)
    db.commit()

    return "Request rejected"
