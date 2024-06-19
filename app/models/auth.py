from pydantic import BaseModel, field_validator, EmailStr
from argon2 import PasswordHasher
from fastapi import HTTPException, status
import re
import jwt
from fastapi import Request, Form
from ..db.mongodb import user_collection
from bson import ObjectId
from ..db.mongodb import db
from fastapi.responses import JSONResponse


class Login(BaseModel):
    email: str
    password: str

    @field_validator("*")
    def str_strip(cls, value):
        return value.strip()


class Register(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_logged_in: bool = True

    @field_validator("*")
    def str_strip(cls, value):
        return value.strip()


class ChangePassword(BaseModel):
    email: str
    old_password: str
    new_password: str

    @field_validator("*")
    def str_strip(cls, value):
        return value.strip()

    @field_validator("*")
    def not_empty(cls, value):
        if not value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Fields cannot be empty",
            )
        return value

    @field_validator("new_password")
    def password_validation(cls, value):
        error = validate_password(value)
        if error:
            return error
        return value


# def validate_email(email):
#     regex = "[\w\.-]+@[\w\.-]+\.\w{2,4}"
#     return re.match(regex, email)


def validate_username(username):
    if not username:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"username": "Username must be provided"},
        )
    if len(username.split(" ")) > 1:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"username": "Username must be a word"},
        )


def validate_password(password):
    if len(password) < 8:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"password": "Password must have at least 8 characters"},
        )
    if not re.search("(?=.*[A-Z])", password):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"password": "Password must have at least one uppercase letter"},
        )
    if not re.search("(?=.*?[a-z])", password):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"password": "Password must have at least one lowercase letter"},
        )
    if not re.search("(?=.*?[0-9])", password):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"password": "Password must have at least one number"},
        )
    if not re.search("(?=.*?[#?!@$%^&*-])", password):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"password": "Password must have at least one special character"},
        )


def get_hashed_password(plaintext):
    ph = PasswordHasher()
    hashed_password = ph.hash(plaintext)
    return hashed_password


def check_password(hashed_password, plaintext):
    try:
        ph = PasswordHasher()
        ph.verify(hashed_password, plaintext)
        return True
    except:
        return False


def generate_token(payload):
    return jwt.encode(payload, "ecommerce", algorithm="HS256")


def get_user(request: Request):
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    token_data = authorization.strip().split(" ")
    if len(token_data) == 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    type = token_data[0]
    token = token_data[1]
    if type != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    payload = jwt.decode(token, "ecommerce", algorithms="HS256")
    user = user_collection.find_one({"_id": ObjectId(payload["_id"])})
    if not user or not user["is_logged_in"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    return payload


def user_dereference(user_dbref):
    user = db.dereference(user_dbref)
    user["_id"] = str(user["_id"])
    del user["password"]
    return user
