import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
from ..models.auth import Token, TokenData
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "08d364d56fa551144ccb0e3ec3c4a2300e7f0269a5a84f43f0454fe7f8486205"
ALGORITHM = "HS256"
EXPIRE_TIME_IN_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=EXPIRE_TIME_IN_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: Token, credential_error):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id = payload.get("user_id")
        if not id:
            raise credential_error
        token_data = TokenData(id=id)
    except PyJWTError:
        raise credential_error
