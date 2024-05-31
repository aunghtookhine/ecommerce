from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from ..models.auth import (
    Register,
    Login,
    get_hashed_password,
    check_password,
    ChangePassword,
)
from ..db.mongodb import user_collection
from ..models.auth import generate_token, check_user
from bson import ObjectId

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
    registered_user = user_collection.find_one({"email": data_dict["email"]})

    if not registered_user or not check_password(
        registered_user["password"], data_dict["password"]
    ):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )

    user_collection.update_one(
        {"email": data_dict["email"]}, {"$set": {"is_logged_in": True}}
    )

    payload = {
        "_id": str(registered_user["_id"]),
        "username": registered_user["username"],
        "email": registered_user["email"],
        "is_logged_in": True,
    }
    token = generate_token(payload)
    return {"token": token, "detail": "Successfully logged in"}


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


@router.patch("/logout", status_code=status.HTTP_200_OK)
def log_out(user=Depends(check_user)):
    updated_user = user_collection.update_one(
        {"_id": ObjectId(user["_id"])}, {"$set": {"is_logged_in": False}}
    )
    if updated_user.acknowledged:
        return {"detail": "Successfully logout"}
