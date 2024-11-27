import uuid
from src.core.authentication import get_current_user, verify_password, create_access_token
from src.models.user import User
from src.schemas.user import CreateUserRequest, LoginRequest, UserResponse, UpdateEmailRequest, UpdateUserRequest
from sqlalchemy.orm import Session
from src.common.custom_responses import AlreadyExists, NotFound, Unauthorized, BadRequest, ForbiddenAccess
from src.models.user import Role
from src.core.authentication import get_password_hash, create_access_token, get_current_user
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
    user = db.query(User).filter(User.id == user_id).first()

    return user.role == Role.ADMIN


def is_director(db: Session, user_id: uuid.UUID) -> bool:
    """
    Check if a user has the director role.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        user_id (uuid.UUID): The UUID of the user to check for the director role.

    Returns:
        bool: True if the user has the director role, False otherwise.
    """
    user = db.query(User).filter(User.id == user_id).first()

    return user.role == Role.DIRECTOR



def get_id_by_username(db: Session, username: str) -> uuid.UUID:

    """
    Retrieve the UUID of a user by its username.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        username (str): The username of the user to retrieve.

    Returns:
        uuid.UUID: The UUID of the user with the specified username.
    """

    user = db.query(User).filter(User.username == username).first()

    return user.id


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
        return NotFound(key="Username", key_value=user.username)

    # if not email_exists(db=db, email=user.email):
    #     return NotFound(key="Email", key_value=user.email")

    db_user = db.query(User).filter(User.username == user.username).first()

    if not verify_password(user.password, db_user.password):
        return Unauthorized(content="Password is incorrect")

    token = create_access_token({"sub": db_user.username})

    return token


def get_user_by_id(db: Session, user_id: uuid.UUID, token: str):
    """
    Retrieve a user from the database by its UUID.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        user_id (uuid.UUID): The UUID of the user to retrieve.
        token (str): The token of the user making the request.

    Returns:
        User: An instance of the `User` class representing the user with the specified UUID.
    """

    user_id = get_id_by_username(db, get_current_user(token))

    if not is_admin(db, user_id):
        return ForbiddenAccess()

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return NotFound(key="User ID", key_value=str(user_id))

    return UserResponse(username=user.username, email=user.email, role=user.role)


def get_me(db: Session, token: str):
    """
    Retrieve the user making the request.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        token (str): The token of the user making the request.

    Returns:
        User: An instance of the `User` class representing the user making the request.
    """

    username = get_current_user(token)

    user = db.query(User).filter(User.username == username).first()

    if not user:
        return NotFound(key="Username", key_value=username)

    return UserResponse(username=user.username, email=user.email, role=user.role)


def get_by_username(db: Session, username: str, token: str):
    """
    Retrieve a user from the database by its username.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        username (str): The username of the user to retrieve.
        token (str): The token of the user making the request.

    Returns:
        User: An instance of the `User` class representing the user with the specified username.
    """

    user = db.query(User).filter(User.username == username).first()

    if not is_admin(db, get_id_by_username(db, get_current_user(token))):
        return ForbiddenAccess()

    if not user:
        return NotFound(key="Username", key_value=username)

    return UserResponse(username=user.username, email=user.email, role=user.role)


def get_by_email(db: Session, email: str, token: str):
    """
    Retrieve a user from the database by its email.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        email (str): The email of the user to retrieve.
        token (str): The token of the user making the request.

    Returns:
        User: An instance of the `User` class representing the user with the specified email.
    """

    user_id = get_id_by_username(db, get_current_user(token))

    if not is_admin(db, user_id):
        return ForbiddenAccess()

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return NotFound(key="Email", key_value=email)

    return UserResponse(username=user.username, email=user.email, role=user.role)


def get_all_users(db: Session, token: str):  # , user_id: uuid.UUID

    """
    Retrieve all users from the database.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        token (str): The token of the user making the request.
    Returns:
        List[User]: A list of all users in the database.
    """

    user_id = get_id_by_username(db, get_current_user(token))

    if not is_admin(db, user_id):
        return ForbiddenAccess()

    if not db.query(User).all():
        return NotFound(key="Users", key_value="")

    users = db.query(User).all()

    return [UserResponse(username=user.username, email=user.email, role=user.role) for user in users]


def update_email(db: Session, new_email: UpdateEmailRequest, token: str) -> UserResponse | AlreadyExists | NotFound:

    """
    Update the email of a user in the database, using the provided UpdateEmailRequest object.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        new_email (UpdateEmailRequest): Contains the new email to be set.
        token (str): The token of the user making the request.

    Returns:
        UserResponse: Contains the updated user details.
    """

    username = get_current_user(token)

    # Fetch the user from the database
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        return NotFound(key="Username", key_value=username)

    # Validate the new email
    if new_email.email:
        if email_exists(db, new_email.email):  # Ensure email is unique
            return AlreadyExists(content="Email")
        db_user.email = new_email.email

    # Commit changes and return the updated user
    db.commit()
    db.refresh(db_user)

    return UserResponse(username=db_user.username, email=db_user.email, role=db_user.role)


def update_user(db: Session, new: UpdateUserRequest, user_to_update: str, token: str) -> (UserResponse |
                                                                                          AlreadyExists |
                                                                                          NotFound |
                                                                                          ForbiddenAccess |
                                                                                          BadRequest):
    """
    Update a user's details in the database.

    Parameters:
        db (Session): An instance of the SQLAlchemy Session class.
        new (UpdateUserRequest): Contains new details for the user.
        user_to_update (str): The username of the user to update.
        token (str): The token of the user making the request.

    Returns:
        UserResponse: The updated user details.
    """

    admin_id = get_id_by_username(db, get_current_user(token))
    if not is_admin(db, admin_id):
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

