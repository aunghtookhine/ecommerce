from pydantic import BaseModel, field_validator, EmailStr
from argon2 import PasswordHasher
from fastapi import HTTPException, status
import re
import jwt
from fastapi import Request, Form
from ..db.mongodb import user_collection
from bson import ObjectId
from ..db.mongodb import db

from dotenv import load_dotenv
import os

load_dotenv(override=True)


class Login(BaseModel):
    email: str
    password: str

    @field_validator("*")
    def str_strip(cls, value):
        return value.strip()

    @field_validator("*")
    def not_empty(cls, value):
        if not value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Fields cannot be empty.",
            )
        return value


class Register(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str
    is_admin: bool = False
    is_logged_in: bool = True

    @field_validator("username", "email", "password", "confirm_password")
    def str_strip(cls, value):
        return value.strip()

    @field_validator("username", "email", "password", "confirm_password")
    def not_empty(cls, value):
        if not value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Fields cannot be empty.",
            )
        return value


class ChangePassword(BaseModel):
    email: str
    old_password: str
    new_password: str
    confirm_password: str

    @field_validator("*")
    def str_strip(cls, value):
        return value.strip()

    @field_validator("*")
    def not_empty(cls, value):
        if not value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Fields cannot be empty.",
            )
        return value


class EditPassword(BaseModel):
    password: str
    confirm_password: str

    @field_validator("*")
    def str_strip(cls, value):
        return value.strip()

    @field_validator("*")
    def not_empty(cls, value):
        if not value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Fields cannot be empty.",
            )
        return value


def validate_username(username):
    if not username:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username must be provided.",
        )
    if len(username.split(" ")) > 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username must be a word.",
        )


def validate_email(email):
    regex = r"[\w\.-]+@[\w\.-]+\.\w{2,4}"
    if not re.match(regex, email):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email must be valid.",
        )


def validate_password(password):
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must have at least 8 characters.",
        )
    if not re.search("(?=.*[A-Z])", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must have at least one uppercase letter.",
        )
    if not re.search("(?=.*?[a-z])", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must have at least one lowercase letter.",
        )
    if not re.search("(?=.*?[0-9])", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must have at least one number.",
        )
    if not re.search("(?=.*?[#?!@$%^&*-])", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must have at least one special character.",
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
    return jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms="HS256")


def get_user(request: Request):
    if request.headers.get("Authorization"):
        authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized1"
        )
    token_data = authorization.strip().split(" ")
    if len(token_data) == 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized2"
        )
    type = token_data[0]
    token = token_data[1]
    if type != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized3"
        )

    payload = decode_token(token)
    user = user_collection.find_one({"_id": ObjectId(payload["_id"])})
    if not user or not user["is_logged_in"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized4"
        )
    return payload


def check_authorization(request: Request):
    authorization = request.headers.get("Authorization")
    token_data = authorization.strip().split(" ")
    payload = decode_token(token_data[1])
    user = user_collection.find_one({"_id": ObjectId(payload["_id"])})
    if not user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You have no access"
        )


def user_dereference(user_dbref):
    user = db.dereference(user_dbref)
    user["_id"] = str(user["_id"])
    del user["password"]
    return user


def check_is_logged_in(request: Request):
    session = request.session
    token = session.get("token")
    if not token:
        return {"is_logged_in": False, "redirect_url": "/login"}
    payload = decode_token(token)
    user = user_collection.find_one({"_id": ObjectId(payload["_id"])})
    if user and user["is_logged_in"]:
        return {
            "is_logged_in": True,
            "is_admin": user["is_admin"],
            "username": user["username"],
        }
    return {"is_logged_in": False, "redirect_url": "/login"}
