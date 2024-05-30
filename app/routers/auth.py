from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from ..models.auth import (
    Register,
    Login,
    validate_email,
    validate_password,
    get_hashed_password,
    check_password,
    ChangePassword,
)
from ..db.mongodb import user_collection
from ..utils.oauth2 import create_token

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(data: Register):
    user_dict = data.model_dump()
    isUsername = user_collection.find_one({"username": user_dict["username"]})
    if isUsername:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username can't be duplicated",
        )

    isEmail = user_collection.find_one({"email": user_dict["email"]})
    if isEmail:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email can't be duplicated"
        )

    user_dict["password"] = get_hashed_password(user_dict["password"])
    user_collection.insert_one(user_dict)
    return {"msg": "Successfully Registered."}


@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(data: Login):
    data_dict = data.model_dump()
    registeredUser = user_collection.find_one({"email": data_dict["email"]})

    if not registeredUser or not check_password(
        registeredUser["password"], data_dict["password"]
    ):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )

    access_token = create_token(data={"user_id": str(registeredUser["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}


@router.patch("/change-password", status_code=status.HTTP_200_OK)
def change_password(data: ChangePassword):
    data_dict = data.model_dump()
    user_docu = user_collection.find_one({"email": data_dict["email"]})
    if not check_password(user_docu["password"], data_dict["old_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong Credentials"
        )
    new_password = get_hashed_password(data_dict["new_password"])
    user = user_collection.update_one(
        {"_id": user_docu["_id"]}, {"$set": {"password": new_password}}
    )
    if user.acknowledged:
        return {"detail": "Successfully Updated."}
