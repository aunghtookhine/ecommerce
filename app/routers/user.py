from fastapi import APIRouter, status, HTTPException
from ..models.user import (
    Register,
    Login,
    validate_email,
    validate_password,
    get_hashed_password,
    check_password,
)
from ..db.mongodb import user_collection

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(data: Register):
    user_dict = data.model_dump()
    isEmail = validate_email(user_dict["email"])
    if not isEmail:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Email"
        )
    isEmail = user_collection.find_one({"email": user_dict["email"]})
    if isEmail:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email can't be duplicated"
        )
    isUsername = user_collection.find_one({"username": user_dict["username"]})
    if isUsername:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username can't be duplicated",
        )
    validate_password(user_dict["password"])

    user_dict["password"] = get_hashed_password(user_dict["password"])
    user_collection.insert_one(user_dict)
    return {"msg": "Successfully Registered."}


@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(data: Login):
    user_dict = data.model_dump()
    registeredUser = user_collection.find_one({"email": user_dict["email"]})
    if registeredUser:
        if check_password(user_dict["password"], registeredUser["password"]):
            return {"msg": f"Welcome {registeredUser['username']}"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
