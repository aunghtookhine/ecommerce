from pydantic import BaseModel
import bcrypt
import email_validator
from fastapi import HTTPException, status
import re


class Login(BaseModel):
    email: str
    password: str


class Register(BaseModel):
    username: str
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str


def validate_email(email):
    try:
        email_validator.validate_email(email)
        return True
    except:
        return False


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


def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode("utf-8"), bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode("utf-8"), hashed_password)
