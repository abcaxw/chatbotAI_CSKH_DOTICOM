from starlette.responses import RedirectResponse

import dconfig

from fastapi import Header, HTTPException, Depends, Request
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

from services import oauth2_scheme

pwd_context = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], deprecated="auto")


async def auth_secret_key(x_auth_token: str = Header()):
    if x_auth_token is None or x_auth_token != dconfig.config_object.SECRET_AUTH_KEY:
        raise HTTPException(status_code=403, detail="Access Denied")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=dconfig.config_object.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, dconfig.config_object.SECRET_AUTH_KEY,
                             algorithm=dconfig.config_object.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str):
    return pwd_context.hash(password)


def get_current_user(request: Request, token: str = None):
    if not token:
        token = request.cookies.get("access_token")
        if not token:
            return RedirectResponse(url="/login", status_code=303)

    try:
        payload = jwt.decode(
            token.split("Bearer ")[-1],  # Tách chữ 'Bearer '
            dconfig.config_object.SECRET_AUTH_KEY,
            algorithms=[dconfig.config_object.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return RedirectResponse(url="/login", status_code=303)
        return user_id
    except JWTError:
        return RedirectResponse(url="/login", status_code=303)
