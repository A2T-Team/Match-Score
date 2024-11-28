import os
from datetime import timedelta, datetime, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
from src.schemas.token import TokenData
from src.models.user import User, Role
from sqlalchemy.orm import Session
from src.api.deps import get_db


load_dotenv()

_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
_ALGORITHM = os.getenv("JWT_ALGORITHM")
_ACCESS_TOKEN_EXPIRE = int(os.getenv("JWT_EXPIRATION"))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token/")


# utility funcs
def verify_password(plain_password: str, hash_password: str):
    return pwd_context.verify(plain_password, hash_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def authenticate_user(
    username: str, password: str, session: Session = Depends(get_db)
) -> User:

    user = session.query(User).filter(User.username == username).first()

    if user is None:
        return None

    hash_password = user.password
    if not verify_password(password, hash_password):
        return None

    return user


def create_access_token(user: User) -> str:
    to_encode = {"user_id": str(user.id)}

    expire = datetime.now(timezone.utc) + timedelta(minutes=_ACCESS_TOKEN_EXPIRE)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, _SECRET_KEY, algorithm=_ALGORITHM)

    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_db)
) -> User:
    credential_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
        user_identifier: str = payload.get("user_id")
        if user_identifier is None:
            raise credential_exception

        TokenData(user_identifier=user_identifier)

    except JWTError:
        raise credential_exception

    user = session.query(User).filter(User.id == user_identifier).first()

    if user is None:
        raise credential_exception

    return user
