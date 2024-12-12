from sqlalchemy.orm import Session
import logging

from typing import List
import uuid

from src.common.custom_responses import AlreadyExists, NotFound, Unauthorized, BadRequest, ForbiddenAccess
from src.core.auth import create_access_token
from src.core.authentication import (get_password_hash, get_current_user, verify_password)

from src.models.user import User, Role
from src.models.request import Requests
from src.models.player import Player
from src.models.tournament import Tournament
from src.models.match import Match

from src.schemas.user import (CreateUserRequest, LoginRequest, UserResponse, UpdateEmailRequest, UpdateUserRequest)


logger = logging.getLogger(__name__)


def is_admin(current_user: User) -> bool:
    """
    Check if a user has the admin role.

    Parameters:
        current_user (User): The user making the request.

    Returns:
        bool: True if the user has the admin role, False otherwise.
    """
    return current_user.role == Role.ADMIN


def is_director(current_user: User) -> bool:
    """
    Check if a user has the director role.

    Parameters:
        current_user (User): The user making the request.

    Returns:
        bool: True if the user has the director role, False otherwise.
    """

    return current_user.role == Role.DIRECTOR


def username_exists(db: Session, username: str) -> bool:

    """
    Check if a user with the provided username already exists in the database.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        username (str): The username to check for existence in the database.

    Returns:
        bool: True if a user with the provided username exists, False otherwise.
    """

    return db.query(User).filter(User.username == username).first() is not None


def email_exists(db: Session, email: str) -> bool:

    """
    Check if a user with the provided email already exists in the database.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        email (str): The email to check for existence in the database.

    Returns:
        bool: True if a user with the provided email exists, False otherwise.
    """

    return db.query(User).filter(User.email == email).first() is not None


def create_user(db: Session, user: CreateUserRequest) -> (str | AlreadyExists):

    """
    Create a new user in the database, using the provided CreateUserRequest object.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        user (CreateUserRequest): An instance of the `CreateUserRequest` class.

    Returns:
        Message: A message indicating the success of the operation.
        Alternatively, an error message if the user does not exist or the user is not authorized.
    """

    if username_exists(db=db, username=user.username):
        return AlreadyExists(content="Username")

    if email_exists(db=db, email=user.email):
        return AlreadyExists(content="Email")

    password = get_password_hash(user.password)

    db_user = User(
        username=user.username,
        password=password,
        email=user.email,
        role=Role.USER
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return "Registration was successfully completed"


def login_user(db: Session, user: LoginRequest) -> (str | Unauthorized):

    """
    Authenticate a user in the database, using the provided CreateUserRequest object.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        user (CreateUserRequest): An instance of the `CreateUserRequest` class.

    Returns:
        Message: A message indicating the success of the operation.
        Alternatively, an error message if the user does not exist or the user is not authorized.
    """

    if not username_exists(db=db, username=user.username):
        return Unauthorized(content="Username or password is incorrect")

    # if not email_exists(db=db, email=user.email):
    #     return NotFound(key="Email", key_value=user.email")

    db_user = db.query(User).filter(User.username == user.username).first()

    if not verify_password(user.password, db_user.password):
        return Unauthorized(content="Username or password is incorrect")

    token = create_access_token(db_user)

    return token


def get_user_by_id(db: Session, user_id: uuid.UUID, current_user: User) -> (UserResponse | NotFound | Unauthorized):

    """
    Retrieve a user from the database by its UUID.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        user_id (uuid.UUID): The UUID of the user to retrieve.
        current_user (User): The user making the request.

    Returns:
        User: An instance of the `UserResponse` class representing the user.
        Alternatively, an error message if the user does not exist or the user is not authorized.
    """

    if current_user is None:
        return Unauthorized()

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return NotFound(key="User ID", key_value=str(user_id))

    return UserResponse(username=user.username, email=user.email, role=user.role)


def get_me(current_user: User) -> (UserResponse | Unauthorized):
    """
    Retrieve the user making the request.

    Parameters:
        current_user (User): The user making the request.

    Returns:
        UserResponse: The details of the user making the request.
        Alternatively, an error message if the user does not exist or the user is not authorized.
    """

    if current_user is None:
        return Unauthorized()

    return UserResponse(username=current_user.username, email=current_user.email, role=current_user.role)


def get_by_username(db: Session, username: str, current_user: User) -> (UserResponse | NotFound | Unauthorized):
    """
    Retrieve a user from the database by its username.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        username (str): The username of the user to retrieve.
        current_user (User): The user making the request.

    Returns:
        UserResponse: An instance of the `UserResponse` class representing the user with the specified username.
        Alternatively, an error message if the user does not exist or the user is not authorized.
    """

    if current_user is None:
        return Unauthorized()

    user = db.query(User).filter(User.username == username).first()

    if not user:
        return NotFound(key="Username", key_value=username)

    return UserResponse(username=user.username, email=user.email, role=user.role)


def get_by_email(db: Session, email: str, current_user: User) -> (UserResponse | NotFound | Unauthorized):
    """
    Retrieve a user from the database by its email.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        email (str): The email of the user to retrieve.
        current_user (User): The user making the request.

    Returns:
        UserResponse: An instance of the `UserResponse` class representing the user with the specified username.
        Alternatively, an error message if the user does not exist or the user is not authorized.
    """

    if current_user is None:
        return Unauthorized()

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return NotFound(key="Email", key_value=email)

    return UserResponse(username=user.username, email=user.email, role=user.role)


def get_all_users(db: Session, current_user: User, limit: int) -> (List[UserResponse] | NotFound | Unauthorized | ForbiddenAccess):

    """
    Retrieve all users from the database.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        current_user (User): The user making the request.
        limit (int): The maximum number of users to return.
    Returns:
        List[User]: A list of all users in the database.
        Alternatively, an error message if no users exist or the user is not authorized.
    """

    if current_user is None:
        return Unauthorized()

    if not current_user.role == Role.ADMIN:
        return ForbiddenAccess()

    if not db.query(User).all():
        return NotFound(key="Users", key_value="")

    users = db.query(User).limit(limit).all()

    return [UserResponse(username=user.username, email=user.email, role=user.role) for user in users]


def update_email(db: Session, new_email: UpdateEmailRequest, current_user: User) -> (UserResponse |
                                                                                     AlreadyExists |
                                                                                     Unauthorized):

    """
    Update the email of a user in the database, using the provided UpdateEmailRequest object.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        new_email (UpdateEmailRequest): Contains the new email to be set.
        current_user (User): The user making the request.

    Returns:
        UserResponse: Contains the updated user details.
        Alternatively, an error message if the user is not authorized.
    """

    if not current_user:
        return Unauthorized()

    if new_email.email:
        if email_exists(db, new_email.email):
            return AlreadyExists(content="Email")
        current_user.email = new_email.email

    db.commit()
    db.refresh(current_user)

    return UserResponse(username=current_user.username, email=current_user.email, role=current_user.role)


def update_user(db: Session, new: UpdateUserRequest, user_to_update: str, current_user: User) -> (UserResponse |
                                                                                                  AlreadyExists |
                                                                                                  Unauthorized |
                                                                                                  NotFound |
                                                                                                  ForbiddenAccess |
                                                                                                  BadRequest):
    """
    Update a user's details in the database.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        new (UpdateUserRequest): Contains new details for the user.
        user_to_update (str): The username of the user to update.
        current_user (User): The user making the request.

    Returns:
        UserResponse: The updated user details.
        Alternatively, an error message if the user is not authorized or the user does not exist.
    """

    if not current_user:
        return Unauthorized()

    if not current_user.role == Role.ADMIN:
        return ForbiddenAccess()

    db_user = db.query(User).filter(User.username == user_to_update).first()
    if not db_user:
        return NotFound(key="Username", key_value=user_to_update)

    if new.email:
        if email_exists(db, new.email):
            return AlreadyExists(content="Email")
        db_user.email = new.email

    if new.role == "admin":
        db_user.role = Role.ADMIN
    elif new.role == "director":
        db_user.role = Role.DIRECTOR
    elif new.role == "player":
        db_user.role = Role.PLAYER
    elif new.role == "user":
        db_user.role = Role.USER

    db.commit()
    db.refresh(db_user)

    return UserResponse(username=db_user.username, email=db_user.email, role=db_user.role)


def delete_user(db: Session, username: str, current_user: User) -> (str | NotFound | Unauthorized | ForbiddenAccess):

    """
    Delete a user from the database.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        username (str): The username of the user to delete.
        current_user (User): The user making the request.

    Returns:
        UserResponse: The details of the deleted user.
        Alternatively, an error message if the user is not authorized or the user does not exist.
    """

    if not current_user:
        return Unauthorized()

    if not current_user.role == Role.ADMIN:
        return ForbiddenAccess()

    user = db.query(User).filter(User.username == username).first()
    if not user:
        return NotFound(key="Username", key_value=username)

    requests = db.query(Requests).filter(Requests.user_id == user.id).all()

    if requests:
        for request in requests:
            db.delete(request)

    players = db.query(Player).filter(Player.user_id == user.id).all()

    if players:
        for player in players:
            player.user_id = None

    tournaments = db.query(Tournament).filter(Tournament.author_id == user.id).all()

    if tournaments:
        for tournament in tournaments:
            tournament.author_id = current_user.id

    matches = db.query(Match).filter(Match.author_id == user.id).all()

    if matches:
        for match in matches:
            match.author_id = current_user.id

    db.delete(user)
    db.commit()

    return f"User {user.username} successfully deleted"
