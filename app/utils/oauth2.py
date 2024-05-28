import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
import datetime as dt
from ..models.auth import Token, TokenData
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..db.mongodb import user_collection
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "08d364d56fa551144ccb0e3ec3c4a2300e7f0269a5a84f43f0454fe7f8486205"
ALGORITHM = "HS256"
EXPIRE_TIME_IN_MINUTES = 30


def create_token(data: dict):
    to_encode = data.copy()
    to_encode.update(
        {"exp": datetime.now(dt.UTC) + timedelta(minutes=EXPIRE_TIME_IN_MINUTES)}
    )
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id: str = payload.get("user_id")
        if not id:
            raise credential_exception
        token_data = TokenData(id=id)
        return token_data
    except PyJWTError:
        raise credential_exception


def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="login"))):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = verify_token(token, credential_exception)
    user = user_collection.find_one({"_id": ObjectId(token.model_dump()["id"])})
    return user
