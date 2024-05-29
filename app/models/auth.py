from pydantic import BaseModel
from argon2 import PasswordHasher
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


class ChangePassword(BaseModel):
    email: str
    old_password: str
    new_password: str


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
