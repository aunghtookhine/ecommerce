from fastapi import APIRouter, status, HTTPException, Depends, Form, Request
from fastapi.responses import RedirectResponse
from ..models.category import Category
from ..db.mongodb import category_collection, db
from bson import ObjectId, DBRef
from ..models.auth import get_user
from ..models.image import image_dereference
from ..models.category import category_dereference
from dotenv import load_dotenv
import os
import math

load_dotenv(override=True)
router = APIRouter()

PAGE_SIZE = 10


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_category(request: Request, data: Category, user=Depends(get_user)):
    try:
        data_dict = data.model_dump()
        if not data_dict["parent_category"] == "null":
            data_dict["parent_category"] = DBRef(
                "categories",
                ObjectId(data_dict["parent_category"]),
                os.getenv("DATABASE_NAME"),
            )
        else:
            data_dict["parent_category"] = None
        if not data_dict["image"] == "null":
            data_dict["image"] = DBRef(
                "images", ObjectId(data_dict["image"]), os.getenv("DATABASE_NAME")
            )
        else:
            data_dict["image"] = None
        category = category_collection.insert_one(data_dict)
        if category.inserted_id:
            return {"detail": "Successfully Created.", "success": True}
    except HTTPException as e:
        return {"detail": e.detail, "success": False}


@router.get("/", status_code=status.HTTP_200_OK)
def find_categories(request: Request, user=Depends(get_user)):
    page = request.query_params.get("page")
    if not page:
        page = 1
    skip = (int(page) - 1) * PAGE_SIZE
    cursor = category_collection.find({}).skip(skip).limit(PAGE_SIZE)
    count = category_collection.count_documents({})
    pages = math.ceil(count / PAGE_SIZE)
    categories = []
    for category in cursor:
        category["_id"] = str(category["_id"])
        if category["parent_category"]:
            category["parent_category"] = category_dereference(
                category["parent_category"]
            )
        category["image"] = image_dereference(category["image"])
        categories.append(category)
    return {"categories": categories, "pages": pages}


@router.get("/parents", status_code=status.HTTP_200_OK)
def find_parent_categories(user=Depends(get_user)):
    cursor = category_collection.find({"parent_category": None})
    parent_categories = []
    for parent_category in cursor:
        parent_category["_id"] = str(parent_category["_id"])
        parent_category["image"] = image_dereference(parent_category["image"])
        parent_categories.append(parent_category)
    return parent_categories


@router.get("/{id}", status_code=status.HTTP_200_OK)
def find_category(id: str, user=Depends(get_user)):
    category = category_collection.find_one({"_id": ObjectId(id.strip())})
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Category Id."
        )
    category["_id"] = str(category["_id"])
    if category["parent_category"]:
        category["parent_category"] = category_dereference(category["parent_category"])
    category["image"] = image_dereference(category["image"])
    return category


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_category(
    id: str,
    data: Category,
    user=Depends(get_user),
):
    try:
        data_dict = data.model_dump()
        if not data_dict["parent_category"] == "null":
            data_dict["parent_category"] = DBRef(
                "categories",
                ObjectId(data_dict["parent_category"]),
                os.getenv("DATABASE_NAME"),
            )
        else:
            data_dict["parent_category"] = None
        if not data_dict["image"] == "null":
            data_dict["image"] = DBRef(
                "images", ObjectId(data_dict["image"]), os.getenv("DATABASE_NAME")
            )
        else:
            data_dict["image"] = None
        category = category_collection.update_one(
            {"_id": ObjectId(id.strip())},
            {"$set": data_dict},
        )
        if not category.matched_count:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Category Id."
            )
        return {"detail": "Successfully Updated.", "success": True}
    except HTTPException as e:
        return {"detail": e.detail, "success": False}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(request: Request, id: str, user=Depends(get_user)):
    try:
        category = category_collection.delete_one({"_id": ObjectId(id.strip())})
        if not category.deleted_count:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Category Id."
            )
    except HTTPException as e:
        return {"detail": e.detail, "success": False}
