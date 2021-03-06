import os
from typing import Optional

from fastapi import APIRouter, status, HTTPException, Header, Response
from .schemas import User, TokenData
from ..utils import token as token_utils
from ..utils.http import HTTPFactory

router = APIRouter()
ACCESS_TOKEN_KEY = os.getenv("ACCESS_TOKEN_KEY")


def raise_401_exception():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect Credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post('/login', status_code=status.HTTP_200_OK)
async def login(request: User):
    credentials = await HTTPFactory.instance.check_user_credentials(request)
    if not credentials:
        raise_401_exception()
    if "username" not in credentials or "id" not in credentials:
        raise_401_exception()
    access_token = token_utils.create_access_token(
        data={"username": request.username, "id": credentials["id"]}
    )
    return {ACCESS_TOKEN_KEY: access_token, "token_type": "bearer"}


@router.post('/credentials', status_code=status.HTTP_200_OK, response_model=TokenData)
async def check_token(response: Response, token: Optional[str] = Header(None), ):
    if not token:
        raise_401_exception()
    token_data = token_utils.verify_token(token)
    if not token_data:
        raise_401_exception()
    response.headers[ACCESS_TOKEN_KEY] = token_utils.refresh_token(token)
    return token_data
