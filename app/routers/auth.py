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
    validate_email,
    EditPassword,
    check_authorization,
)
from ..db.mongodb import user_collection
from ..models.auth import generate_token, get_user
from bson import ObjectId
from fastapi.templating import Jinja2Templates
from ..db.mongodb import product_collection
from pymongo import UpdateOne
import math

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
PAGE_SIZE = 10


@router.get("/users", status_code=status.HTTP_200_OK)
def find_users(
    request: Request, user=Depends(get_user), check_auth=Depends(check_authorization)
):
    q = request.query_params.get("q")
    page = request.query_params.get("page")
    if not page:
        page = 1
    skip = (int(page) - 1) * PAGE_SIZE
    if q != None:
        cursor = (
            user_collection.find(
                {
                    "$or": [
                        {"username": {"$regex": q, "$options": "i"}},
                        {"email": {"$regex": q, "$options": "i"}},
                    ]
                }
            )
            .skip(skip)
            .limit(PAGE_SIZE)
        )
        count = user_collection.count_documents(
            {
                "$or": [
                    {"username": {"$regex": q, "$options": "i"}},
                    {"email": {"$regex": q, "$options": "i"}},
                ]
            }
        )
    else:
        cursor = user_collection.find({}).skip(skip).limit(PAGE_SIZE)
        count = user_collection.count_documents({})

    pages = math.ceil(count / PAGE_SIZE)
    users = []
    for user in cursor:
        user["_id"] = ObjectId(user["_id"])
        del user["password"]
        users.append(user)
    return {"users": users, "pages": pages}


@router.get("/users/{id}", status_code=status.HTTP_200_OK)
def find_user(id: str, user=Depends(get_user), check_auth=Depends(check_authorization)):
    user = user_collection.find_one({"_id": ObjectId(id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid User Id."
        )
    user["_id"] = str(user["_id"])
    del user["password"]
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(request: Request, data: Register):
    try:
        user_dict = data.model_dump()
        validate_username(user_dict["username"])
        isUsername = user_collection.find_one({"username": user_dict["username"]})
        if isUsername:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username can't be duplicated.",
            )

        validate_email(user_dict["email"])

        isEmail = user_collection.find_one({"email": user_dict["email"]})
        if isEmail:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email can't be duplicated.",
            )
        if user_dict["password"] != user_dict["confirm_password"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Password and Confirm Password must be same.",
            )
        validate_password(user_dict["password"])

        user_dict["password"] = get_hashed_password(user_dict["password"])
        del user_dict["confirm_password"]
        new_user = user_collection.insert_one(user_dict)
        if new_user.inserted_id:
            if not request.headers.get("Authorization"):
                payload = {
                    "_id": str(new_user.inserted_id),
                    "username": user_dict["username"],
                }
                token = generate_token(payload)
                request.session["token"] = token
            return {"detail": "Successfully Registered.", "success": True}
    except HTTPException as e:
        print(e)
        return {"detail": e.detail, "success": False}


@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(request: Request, data: Login):
    try:
        data_dict = data.model_dump()
        registered_user = user_collection.find_one({"email": data_dict["email"]})

        if not registered_user or not check_password(
            registered_user["password"], data_dict["password"]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials."
            )
        user = user_collection.update_one(
            {"email": data_dict["email"]}, {"$set": {"is_logged_in": True}}
        )
        payload = {
            "_id": str(registered_user["_id"]),
            "username": registered_user["username"],
        }
        token = generate_token(payload)
        if user.matched_count:
            request.session["token"] = token
            url = "/"
            if registered_user["is_admin"]:
                url = "/dashboard/checkouts"
            return {"detail": "Successfully Logged In.", "success": True, "url": url}
    except HTTPException as e:
        return {"detail": e.detail, "success": False}


@router.patch("/change-password", status_code=status.HTTP_200_OK)
def change_password(data: ChangePassword, user=Depends(get_user)):
    try:
        data_dict = data.model_dump()
        validate_email(data_dict["email"])
        user = user_collection.find_one({"_id": ObjectId(user["_id"])})
        if not data_dict["email"] == user["email"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You must enter your email.",
            )
        if not check_password(user["password"], data_dict["old_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong Credentials"
            )
        if not data_dict["new_password"] == data_dict["confirm_password"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="New Password and Confirm Password must be same.",
            )
        if check_password(user["password"], data_dict["new_password"]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Please provide new password",
            )
        validate_password(data_dict["new_password"])
        new_password = get_hashed_password(data_dict["new_password"])
        user = user_collection.update_one(
            {"_id": user["_id"]}, {"$set": {"password": new_password}}
        )
        if user.acknowledged:
            return {"detail": "Successfully Changed Password.", "success": True}
    except HTTPException as e:
        return {"detail": e.detail, "success": False}


@router.patch("/{id}", status_code=status.HTTP_200_OK)
def edit_password(
    id: str,
    data: EditPassword,
    user=Depends(get_user),
    check_auth=Depends(check_authorization),
):
    try:
        data_dict = data.model_dump()
        if not data_dict["password"] == data_dict["confirm_password"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Password and Confirm Password must be same.",
            )
        user = user_collection.find_one({"_id": ObjectId(user["_id"])})
        if check_password(user["password"], data_dict["password"]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Please provide new password.",
            )
        validate_password(data_dict["password"])
        new_password = get_hashed_password(data_dict["password"])
        user = user_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"password": new_password}},
        )
        if user.acknowledged:
            return {"detail": "Successfully Changed Password.", "success": True}
    except HTTPException as e:
        return {"detail": e.detail, "success": False}


@router.post("/logout", status_code=status.HTTP_200_OK)
def log_out(request: Request, user=Depends(get_user)):
    try:
        updated_user = user_collection.update_one(
            {"_id": ObjectId(user["_id"])}, {"$set": {"is_logged_in": False}}
        )
        if updated_user.matched_count:
            clear_session(request)
            return {"detail": "Successfully Logged Out.", "success": True}
    except HTTPException as e:
        return {"detail": e.detail, "success": False}


@router.get("/clear")
def clear_session(request: Request, user=Depends(get_user)):
    session = request.session
    cart_items = session.get("cart")
    if cart_items:
        operations = []
        for product_id, qty in cart_items.items():
            operations.append(
                UpdateOne({"_id": ObjectId(product_id)}, {"$inc": {"item": qty}})
            )
        result = product_collection.bulk_write(operations)
        if not result.bulk_api_result.get("writeErrors"):
            session.pop("cart", None)
    session.clear()
    return {"detail": "Successfully Cleared."}
