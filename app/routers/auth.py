from fastapi import APIRouter, status, HTTPException, Depends, Request
from fastapi.responses import Response
from ..models.auth import (
    Register,
    Login,
    get_hashed_password,
    check_password,
    ChangePassword,
)
from ..db.mongodb import user_collection
from ..models.auth import generate_token, get_user
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
    new_user = user_collection.insert_one(user_dict)
    payload = {"_id": str(new_user.inserted_id)}
    token = generate_token(payload)
    return {"detail": "Successfully Registered.", "token": token}


@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(request: Request, response: Response, data: Login):
    # = Depends(Login.form_format)
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

    payload = {"_id": str(registered_user["_id"])}

    token = generate_token(payload)
    # res = RedirectResponse(url="/", status_code=303)
    # res.set_cookie(key="token", value=token)
    return {"detail": "Successfully login", "token": token}


@router.patch("/change-password", status_code=status.HTTP_200_OK)
def change_password(data: ChangePassword, user=Depends(get_user)):
    data_dict = data.model_dump()
    user = user_collection.find_one({"_id": ObjectId(user["_id"])})
    if not data_dict["email"] == user["email"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="You must enter your email"
        )
    user_docu = user_collection.find_one({"email": data_dict["email"]})
    if not check_password(user_docu["password"], data_dict["old_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong Credentials"
        )
    if check_password(user_docu["password"], data_dict["new_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide new password",
        )
    new_password = get_hashed_password(data_dict["new_password"])
    user = user_collection.update_one(
        {"_id": user_docu["_id"]}, {"$set": {"password": new_password}}
    )
    if user.acknowledged:
        return {"detail": "Successfully Updated."}


@router.get("/logout", status_code=status.HTTP_200_OK)
def log_out(user=Depends(get_user)):
    updated_user = user_collection.update_one(
        {"_id": ObjectId(user["_id"])}, {"$set": {"is_logged_in": False}}
    )
    if updated_user.matched_count:
        return {"detail": "Successfully logged out"}
    # return RedirectResponse(url="/login")
