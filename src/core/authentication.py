import os
from datetime import timedelta, datetime, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
from src.models.user import User
from src.core.config import Settings


load_dotenv()

settings = Settings()

_SECRET_KEY = settings.JWT_SECRET_KEY
_ALGORITHM = settings.JWT_ALGORITHM
_ACCESS_TOKEN_EXPIRE = settings.JWT_EXPIRATION


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


# utility funcs
def verify_password(plain_password: str, hash_password: str):
    return pwd_context.verify(plain_password, hash_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    user = User.query.filter_by(username=username).first()

    if user is None:
        return False

    if not verify_password(password, user.password):
        return False

    return user.id


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=_ACCESS_TOKEN_EXPIRE)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, _SECRET_KEY, algorithm=_ALGORITHM)

    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credential_exception

    except JWTError:
        raise credential_exception

    return username
