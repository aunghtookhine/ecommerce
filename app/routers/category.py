from fastapi import APIRouter, status, HTTPException, Depends
from ..models.category import Category
from ..db.mongodb import image_collection, category_collection, db
from bson import ObjectId
from ..models.auth import get_user

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_category(data: Category, user=Depends(get_user)):
    data_dict = data.model_dump()
    if data_dict["parent_id"]:
        data_dict["parent_id"] = {
            "$ref": "categories",
            "$id": ObjectId(data_dict["parent_id"]),
            "$db": "ecommerce",
        }
    category = category_collection.insert_one(
        {
            "name": data_dict["name"],
            "parent_id": data_dict["parent_id"],
            "image": {
                "$ref": "images",
                "$id": data_dict["image_id"],
                "$db": "ecommerce",
            },
        }
    )

    # category_with_image = category_collection.find_one({"_id": category.inserted_id})
    # image_reference = category_with_image["image"]
    # image = image_collection.find_one({"_id": ObjectId(image_reference.id)})
    # print(image)
    # return
    # return {"_id": str(category.inserted_id)}


@router.get("/", status_code=status.HTTP_200_OK)
def find_categories(user=Depends(get_user)):
    cursor = category_collection.find({})
    categories = []
    for category in cursor:
        category["_id"] = str(category["_id"])
        categories.append(category)
    return categories


@router.get("/parents", status_code=status.HTTP_200_OK)
def find_parent_categories(user=Depends(get_user)):
    cursor = category_collection.find({"parent_category": "0"})
    parent_categories = []
    for parent_category in cursor:
        parent_category["_id"] = str(parent_category["_id"])
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
    return category


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_category(id: str, data: Category, user=Depends(get_user)):
    category = category_collection.update_one(
        {"_id": ObjectId(id.strip())}, {"$set": data.model_dump()}
    )
    if not category.matched_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Category Id"
        )
    return {"detail": "Successfully Updated"}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(id: str, user=Depends(get_user)):
    category = category_collection.delete_one({"_id": ObjectId(id.strip())})
    if not category.deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Category Id"
        )
