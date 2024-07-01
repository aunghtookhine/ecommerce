from fastapi import APIRouter, status, HTTPException, Depends, Form, Request
from fastapi.responses import RedirectResponse
from ..models.category import Category
from ..db.mongodb import category_collection, db
from bson import ObjectId, DBRef
from ..models.auth import get_user
from ..models.image import image_dereference
from ..models.category import category_dereference

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_category(
    request: Request,
    data: Category = Depends(Category.to_form_data),
    token: str = Form(...),
):
    user = get_user(request, token)
    data_dict = data.model_dump()
    if data_dict["parent_category"]:
        data_dict["parent_category"] = DBRef(
            "categories", ObjectId(data_dict["parent_category"]), "ecommerce"
        )
    if data_dict["image"]:
        data_dict["image"] = DBRef("images", ObjectId(data_dict["image"]), "ecommerce")
    category = category_collection.insert_one(data_dict)
    if category.inserted_id:
        return RedirectResponse(
            "/dashboard/categories", status_code=status.HTTP_302_FOUND
        )


@router.get("/", status_code=status.HTTP_200_OK)
def find_categories(user=Depends(get_user)):
    cursor = category_collection.find({})
    categories = []
    for category in cursor:
        category["_id"] = str(category["_id"])
        if category["parent_category"]:
            category["parent_category"] = category_dereference(
                category["parent_category"]
            )
        category["image"] = image_dereference(category["image"])
        categories.append(category)
    return categories


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
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Category Id"
        )
    category["_id"] = str(category["_id"])
    if category["parent_category"]:
        category["parent_category"] = category_dereference(category["parent_category"])
    category["image"] = image_dereference(category["image"])
    return category


@router.post("/{id}", status_code=status.HTTP_200_OK)
def update_category(
    request: Request,
    id: str,
    token: str = Form(...),
    data: Category = Depends(Category.to_form_data),
):
    user = Depends(get_user(request, token))
    data_dict = data.model_dump()
    if data_dict["parent_category"]:
        data_dict["parent_category"] = DBRef(
            "categories", ObjectId(data_dict["parent_category"]), "ecommerce"
        )
    if data_dict["image"]:
        data_dict["image"] = DBRef("images", ObjectId(data_dict["image"]), "ecommerce")

    category = category_collection.update_one(
        {"_id": ObjectId(id.strip())},
        {"$set": data_dict},
    )
    if not category.matched_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Category Id"
        )
    # return RedirectResponse("/dashboard/categories", status_code=status.HTTP_302_FOUND)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(id: str, user=Depends(get_user)):
    category = category_collection.delete_one({"_id": ObjectId(id.strip())})
    if not category.deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Category Id"
        )
