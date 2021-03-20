from typing import Optional

from fastapi import APIRouter, status, HTTPException, Header
from .schemas import User
from ..utils import token, http

router = APIRouter()


def raise_401_exception():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect Credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post('/login', status_code=status.HTTP_200_OK)
async def login(request: User):
    credentials_status_code = await http.check_user_credentials(request)
    if credentials_status_code == status.HTTP_401_UNAUTHORIZED:
        raise_401_exception()
    if credentials_status_code == status.HTTP_200_OK:
        access_token = token.create_access_token(
            data={"sub": request.email}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Credential Service Error"
    )


@router.post('/credentials', status_code=status.HTTP_200_OK)
async def check_token(access_token: Optional[str] = Header(None)):
    if not access_token:
        raise_401_exception()
    if not token.verify_token(access_token):
        raise_401_exception()
    return "OK"
