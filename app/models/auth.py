from pydantic import BaseModel, field_validator
from argon2 import PasswordHasher
from fastapi import HTTPException, status, Form
import re
import jwt
from fastapi import Request
from ..db.mongodb import user_collection
from bson import ObjectId


class Login(BaseModel):
    email: str
    password: str

    @field_validator("*")
    def str_strip(cls, value):
        return value.strip()

    @classmethod
    def form_format(cls, email: str = Form(...), password: str = Form(...)):
        return cls(email=email, password=password)


class Register(BaseModel):
    username: str
    email: str
    password: str
    is_logged_in: bool = False

    @field_validator("*")
    def str_strip(cls, value):
        return value.strip()

    @field_validator("username")
    def username_validation(cls, value):
        if not value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Username must be provided",
            )
        if len(value.split(" ")) > 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Username must be a word",
            )
        return value

    @field_validator("email")
    def email_validation(cls, value):
        if not validate_email(value):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid Email"
            )
        return value

    @field_validator("password")
    def password_validation(cls, value):
        validate_password(value)
        return value


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
        validate_password(value)
        return value


def validate_email(email):
    regex = "[\w\.-]+@[\w\.-]+\.\w{2,4}"
    return re.match(regex, email)


def validate_password(password):
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must have at least 8 characters",
        )
    if not re.search("(?=.*[A-Z])", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must have at least one uppercase letter",
        )
    if not re.search("(?=.*?[a-z])", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must have at least one lowercase letter",
        )
    if not re.search("(?=.*?[0-9])", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must have at least one number",
        )
    if not re.search("(?=.*?[#?!@$%^&*-])", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must have at least one special character",
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
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    payload = jwt.decode(token, "ecommerce", algorithms="HS256")
    user = user_collection.find_one({"_id": ObjectId(payload["_id"])})
    if not user["is_logged_in"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    return payload
