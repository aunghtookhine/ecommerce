from fastapi import APIRouter, status, HTTPException
from ..models.category import Category
from ..db.mongodb import category_collection
from bson import ObjectId

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_category(data: Category):
    category_dict = data.model_dump()
    category = category_collection.insert_one(category_dict)
    if not category.acknowledged:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)


@router.get("/", status_code=status.HTTP_200_OK)
def find_categories():
    cursor = category_collection.find({})
    categories = []
    for category in cursor:
        category["_id"] = str(category["_id"])
        categories.append(category)
    return categories


@router.get("/{id}", status_code=status.HTTP_200_OK)
def find_category(id: str):
    category = category_collection.find_one({"_id": ObjectId(id)})
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Category Id"
        )
    category["_id"] = str(category["_id"])
    return category


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_category(id: str, data: Category):
    category = category_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": data.model_dump()}
    )
    if not category.matched_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Category Id"
        )
    return {"detail": "Successfully Updated"}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(id: str):
    category = category_collection.delete_one({"_id": ObjectId(id)})
    if not category.deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Category Id"
        )
