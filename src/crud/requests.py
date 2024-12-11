from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import uuid
import re

from src.common.custom_responses import NotFound, BadRequest, ForbiddenAccess, Unauthorized

from src.models.request import RequestType, Requests, RequestStatus, RequestAction
from src.models.user import User, Role
from src.models.player import Player

from src.schemas.request import CreateRequest, RequestResponse

from src.crud.players import update_player_with_user


logger = logging.getLogger(__name__)


def creating_request(db: Session, request: CreateRequest, current_user: User, r_type: RequestType) -> (RequestResponse |
                                                                                                       Unauthorized |
                                                                                                       NotFound |
                                                                                                       BadRequest):

    """
    Create a new request in the database.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        request (CreateRequest): Contains the details of the request.
        current_user (User): The user making the request.
        r_type (RequestType): The type of request to create.

    Returns:
        RequestResponse: The details of the created request.
        Alternatively, a NotFound or BadRequest response.
    """

    if current_user is None:
        return Unauthorized()

    if current_user.role == Role.ADMIN:
        return BadRequest("Admins cannot make requests")

    db_request = Requests(
        user_id=current_user.id,
        type=r_type,
        reason=request.reason
    )

    if db_request.type == RequestType.PROMOTE and current_user.role == Role.DIRECTOR:
        return BadRequest("You are already a director")

    if db_request.type == RequestType.DEMOTE and current_user.role == Role.USER:
        return BadRequest("There is no role to demote to")

    if db_request.type == RequestType.LINK:
        potential_player = db.query(Player).filter(Player.user_id == current_user.id).first()
        if potential_player:
            return BadRequest("You are already linked to a player")
        if not re.match(r"[a-zA-Z]+\s[a-zA-Z]+", request.reason):
            return BadRequest("Invalid player name format")

        firstname, lastname = request.reason.split(" ")
        player = db.query(Player).filter(Player.first_name == firstname, Player.last_name == lastname).first()

        if not player:
            return NotFound(key="Player", key_value=request.reason)

    if db_request.type == RequestType.UNLINK:
        player = db.query(Player).filter(Player.user_id == current_user.id).first()
        if not player:
            return BadRequest("You are not linked to any player")

    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    return RequestResponse(id=db_request.id, created_at=db_request.created_at,
                           type=db_request.type.value, user_id=db_request.user_id,
                           reason=db_request.reason, status=db_request.status)


def view_requests(db: Session, current_user: User, search: Optional[str]) -> (List[RequestResponse] |
                                                                              Unauthorized |
                                                                              NotFound |
                                                                              BadRequest |
                                                                              ForbiddenAccess):

    """
    Retrieve all requests from the database.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        current_user (User): The user making the request.
        search (Optional[str]): The status of the requests to retrieve.

    Returns:
        List[RequestResponse]: A list of all requests in the database.
        Alternatively, an Unauthorized, NotFound, or ForbiddenAccess response.
    """

    if current_user is None:
        return Unauthorized()

    if not current_user.role == Role.ADMIN:
        return ForbiddenAccess()

    if not db.query(Requests).all():
        return NotFound(key="Requests", key_value="")

    if search:
        requests = db.query(Requests).filter(Requests.status == search).all()
        if not requests:
            return NotFound(key="Requests", key_value="")

    else:
        requests = db.query(Requests).all()

    return [RequestResponse(id=request.id, created_at=request.created_at, type=request.type.value,
                            user_id=request.user_id, reason=request.reason, status=request.status)
            for request in requests]


def open_request(db: Session, request_id: uuid.UUID, current_user: User, action) -> (RequestResponse |
                                                                                     Unauthorized |
                                                                                     NotFound |
                                                                                     ForbiddenAccess |
                                                                                     BadRequest):

    """
    Retrieve a request from the database by its ID.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        request_id (uuid.UUID): The ID of the request to retrieve.
        current_user (User): The user making the request.
        action: The action to be taken on the request.

    Returns:
        RequestResponse: The details of the requested request.
        Alternatively, an Unauthorized, NotFound, or ForbiddenAccess response.
    """

    if current_user is None:
        return Unauthorized()

    if not current_user.role == Role.ADMIN:
        return ForbiddenAccess()

    request = db.query(Requests).filter(Requests.id == request_id).first()

    if not request:
        return NotFound(key="Request ID", key_value=str(request_id))

    if request.status != RequestStatus.PENDING and action:
        return BadRequest("Cannot perform action on request, that is already accepted or rejected")

    if action == RequestAction.ACCEPT:
        return accept_request(db, request)

    if action == RequestAction.REJECT:
        return reject_request(db, request)

    return RequestResponse(id=request.id, created_at=request.created_at, type=request.type.value,
                           user_id=request.user_id, reason=request.reason, status=request.status)


def accept_request(db, request: Requests) -> (str |
                                              Unauthorized |
                                              NotFound |
                                              BadRequest |
                                              ForbiddenAccess):

    """
    Accept a request in the database.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        request (Request): The request to accept.

    Returns:
        str: A message indicating the request was successfully accepted.
        Alternatively, an Unauthorized, NotFound, BadRequest, or ForbiddenAccess response.
    """

    user = db.query(User).filter(User.id == request.user_id).first()

    if request.type == RequestType.PROMOTE:
        user.role = Role.DIRECTOR

    if request.type == RequestType.DEMOTE:
        user.role = Role.USER

    if request.type == RequestType.LINK:

        firstname, lastname = request.reason.split(" ")
        player = db.query(Player).filter(Player.first_name == firstname, Player.last_name == lastname).first()

        update_player_with_user(db, player.id, request.user_id)

    if request.type == RequestType.UNLINK:
        player = db.query(Player).filter(Player.user_id == request.user_id).first()
        player.user_id = None

    request.status = RequestStatus.ACCEPTED

    db.commit()
    db.refresh(request)

    return f"{request.type.value} from {user.username} accepted"


def reject_request(db, request: Requests) -> (str |
                                              Unauthorized |
                                              NotFound |
                                              ForbiddenAccess):

    """
    Reject a request in the database.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        request (Request): The request to accept.

    Returns:
        str: A message indicating the request was successfully rejected.
        Alternatively, an Unauthorized, NotFound, or ForbiddenAccess response.
    """

    user = db.query(User).filter(User.id == request.user_id).first()

    request.status = RequestStatus.REJECTED

    db.commit()
    db.refresh(request)

    return f"{request.type.value} from {user.username} rejected"
