from fastapi import APIRouter, status, HTTPException, Depends, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from ..models.auth import (
    Register,
    Login,
    get_hashed_password,
    check_password,
    ChangePassword,
    validate_password,
    validate_username,
)
from ..db.mongodb import user_collection
from ..models.auth import generate_token, get_user
from ..routers.cart import clear_session
from bson import ObjectId
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(request: Request, data: Register):
    user_dict = data.model_dump()
    error = validate_username(user_dict["username"])
    if error:
        return error
    isUsername = user_collection.find_one({"username": user_dict["username"]})
    if isUsername:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"username": "Username can't be duplicated"},
        )

    isEmail = user_collection.find_one({"email": user_dict["email"]})
    if isEmail:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"email": "Email can't be duplicated"},
        )
    error = validate_password(user_dict["password"])
    if error:
        return error
    user_dict["password"] = get_hashed_password(user_dict["password"])
    new_user = user_collection.insert_one(user_dict)
    payload = {"_id": str(new_user.inserted_id)}
    token = generate_token(payload)
    request.session["user_id"] = str(new_user.inserted_id)
    return {"detail": "Successfully Registered.", "token": token}


@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(request: Request, data: Login):
    data_dict = data.model_dump()
    registered_user = user_collection.find_one({"email": data_dict["email"]})

    if not registered_user or not check_password(
        registered_user["password"], data_dict["password"]
    ):
        return JSONResponse(content={"error": "Invalid Credentials"}, status_code=401)
    user = user_collection.update_one(
        {"email": data_dict["email"]}, {"$set": {"is_logged_in": True}}
    )
    payload = {"_id": str(registered_user["_id"])}
    token = generate_token(payload)
    if user.matched_count:
        request.session["user_id"] = str(registered_user["_id"])
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
def log_out(request: Request, user=Depends(get_user)):
    updated_user = user_collection.update_one(
        {"_id": ObjectId(user["_id"])}, {"$set": {"is_logged_in": False}}
    )
    if updated_user.matched_count:
        clear_session(request)
        return {"detail": "Successfully logged out"}
