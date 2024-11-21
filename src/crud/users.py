import uuid
from src.core.authentication import get_current_user, verify_password, create_access_token
from src.models.user import User
from src.schemas.user import CreateUserRequest, LoginRequest
from sqlalchemy.orm import Session
from src.common.custom_responses import AlreadyExists, NotFound, Unauthorized
import logging

logger = logging.getLogger(__name__)


def is_admin(db: Session, user_id: uuid.UUID) -> bool:
    """
    Check if a user has the admin role.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        user_id (uuid.UUID): The UUID of the user to check for the admin role.

    Returns:
        bool: True if the user has the admin role, False otherwise.
    """

    return db.query(User).filter(User.id == user_id, User.role == "admin").first() is not None


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


def create_user(db: Session, user: CreateUserRequest):
    """
    Create a new user in the database, using the provided CreateUserRequest object.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        user (CreateUserRequest): An instance of the `CreateUserRequest` class.

    Returns:
        User: An instance of the `User` class with all attributes of the newly created user.
    """

    if username_exists(db=db, username=user.username):
        return AlreadyExists(content="Username already exists")

    if email_exists(db=db, email=user.email):
        return AlreadyExists(content="Email already exists")



    db_user = User(
        username=user.username,
        password=user.password,
        email=user.email,
        role=user.role,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def login_user(db: Session, user: LoginRequest):

    """
    Authenticate a user in the database, using the provided CreateUserRequest object.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        user (CreateUserRequest): An instance of the `CreateUserRequest` class.

    Returns:
        User: An instance of the `User` class with all attributes of the newly created user.
    """

    if not username_exists(db=db, username=user.username):
        return NotFound(content="Username does not exist")

    # if not email_exists(db=db, email=user.email):
    #     return NotFound(content="Email does not exist")

    db_user = db.query(User).filter(User.username == user.username).first()

    if not verify_password(user.password, db_user.password):
        return Unauthorized(content="Password is incorrect")

    token = create_access_token({"sub": db_user.username})
    return token

def get_user_by_id(db: Session, user_id: uuid.UUID):
    """
    Retrieve a user from the database by its UUID.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        user_id (uuid.UUID): The UUID of the user to retrieve.

    Returns:
        User: An instance of the `User` class representing the user with the specified UUID.
    """

    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    """
    Retrieve a user from the database by its username.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        username (str): The username of the user to retrieve.

    Returns:
        User: An instance of the `User` class representing the user with the specified username.
    """

    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    """
    Retrieve a user from the database by its email.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        email (str): The email of the user to retrieve.

    Returns:
        User: An instance of the `User` class representing the user with the specified email.
    """

    return db.query(User).filter(User.email == email).first()


def get_all_users(db: Session):  # , user_id: uuid.UUID

    """
    Retrieve all users from the database.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        user_id (uuid.UUID): The UUID of the user making the request.

    Returns:
        List[User]: A list of all users in the database.
    """

    # if not is_admin(db, user_id):
    #     return "You are not authorized to view this data"
    #
    # if not db.query(User).all():
    #     return NotFound(content="No users found")

    return db.query(User).all()
