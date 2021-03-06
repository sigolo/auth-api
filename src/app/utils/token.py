import os
from datetime import timedelta, datetime

from jose import jwt, JWTError

from ..api.schemas import TokenData

SECRET_KEY = os.getenv("SECRET_JWT_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRATION_MINUTES"))


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username_key = os.getenv("USERNAME_RETURN_KEY")
        id_key = os.getenv("ID_RETURN_KEY")
        username: str = payload.get(username_key) if username_key and username_key in payload \
            else payload.get("username")
        user_id: str = payload.get(id_key) if id_key and id_key in payload \
            else payload.get("id")
        print(payload)
        if username is None:
            return False
        return TokenData(username=username, user_id=user_id)
    except JWTError as e:
        print(e)
        return False


def refresh_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return create_access_token({"username": payload.get("username"), "id": payload.get("id")})
