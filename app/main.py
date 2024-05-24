from fastapi import FastAPI, HTTPException, status
from .db.mongodb import get_mongo_client
from dotenv import load_dotenv
import os
from .models.user import (
    Register,
    Login,
    validate_email,
    validate_password,
    get_hashed_password,
    check_password,
)
from .models.category import Category

app = FastAPI()
load_dotenv()

app.database = get_mongo_client(
    os.getenv("MONGO_URI"),
    os.getenv("DATABASE_NAME"),
)


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(data: Register):
    user_dict = data.model_dump()
    isEmail = validate_email(user_dict["email"])
    if not isEmail:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Email"
        )
    isEmail = app.database["users"].find_one({"email": user_dict["email"]})
    if isEmail:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email can't be duplicated"
        )
    isUsername = app.database["users"].find_one({"username": user_dict["username"]})
    if isUsername:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username can't be duplicated",
        )
    validate_password(user_dict["password"])

    user_dict["password"] = get_hashed_password(user_dict["password"])
    app.database["users"].insert_one(user_dict)
    return {"msg": "Successfully Registered."}


@app.post("/login", status_code=status.HTTP_200_OK)
def login_user(data: Login):
    user_dict = data.model_dump()
    registeredUser = app.database["users"].find_one({"email": user_dict["email"]})
    if registeredUser:
        if check_password(user_dict["password"], registeredUser["password"]):
            return {"msg": f"Welcome {registeredUser['username']}"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@app.post("/category", status_code=status.HTTP_201_CREATED)
def create_category(data: Category):
    category_dict = data.model_dump()
    app.database["category"].insert_one(category_dict)


@app.get("/category/{id}", status_code=status.HTTP_200_OK)
def find_category(id):
    category = app.database["category"].find_one({"_id": id})
    print(category)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Category Id"
        )
    return category
