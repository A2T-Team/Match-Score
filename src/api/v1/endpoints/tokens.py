from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas.token import Token
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.models.user import User, Role
from src.core.auth import authenticate_user, create_access_token

router = APIRouter()


@router.post("/")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
    """
    Authenticate the user and return an access token.

    Parameters:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.

    Returns:
        Token: An access token if authentication is successful, or an HTTPException if authentication fails.
    """

    user = authenticate_user(form_data.username, form_data.password, session)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user=user)
    return Token(access_token=access_token, token_type="bearer")
