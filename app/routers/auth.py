from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from ..models.auth import (
    Register,
    validate_email,
    validate_password,
    get_hashed_password,
    check_password,
)
from ..db.mongodb import user_collection
from ..utils.oauth2 import create_token

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(data: Register):
    user_dict = data.model_dump()
    user_dict["username"] = user_dict["username"].strip()
    user_dict["password"] = user_dict["password"].strip()
    user_dict["email"] = user_dict["email"].strip()

    if not user_dict["username"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username must be provided"
        )

    if len(user_dict["username"].split(" ")) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username must be a word"
        )

    isEmail = validate_email(user_dict["email"])
    if not isEmail:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Email"
        )
    isEmail = user_collection.find_one({"email": user_dict["email"]})
    if isEmail:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email can't be duplicated"
        )
    isUsername = user_collection.find_one({"username": user_dict["username"]})
    if isUsername:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username can't be duplicated",
        )
    validate_password(user_dict["password"])

    user_dict["password"] = get_hashed_password(user_dict["password"])
    user_collection.insert_one(user_dict)
    return {"msg": "Successfully Registered."}


@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(data: OAuth2PasswordRequestForm = Depends()):
    registeredUser = user_collection.find_one({"email": data.username})
    if not registeredUser or not check_password(
        data.password, registeredUser["password"]
    ):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    access_token = create_token(data={"user_id": str(registeredUser["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}
