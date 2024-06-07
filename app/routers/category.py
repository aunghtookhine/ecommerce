from fastapi import APIRouter, status, HTTPException, Depends
from ..models.category import Category
from ..db.mongodb import image_collection, category_collection, db
from bson import ObjectId, DBRef
from ..models.auth import get_user
from ..models.image import image_dereference
from ..models.category import category_dereference

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_category(data: Category, user=Depends(get_user)):
    data_dict = data.model_dump()
    if data_dict["parent_id"]:
        data_dict["parent_id"] = DBRef(
            "categories", ObjectId(data_dict["parent_id"]), "ecommerce"
        )
    category = category_collection.insert_one(
        {
            "name": data_dict["name"],
            "parent_category": data_dict["parent_id"],
            "image": DBRef("images", ObjectId(data_dict["image_id"]), "ecommerce"),
        }
    )
    return {"_id": str(category.inserted_id)}


@router.get("/", status_code=status.HTTP_200_OK)
def find_categories(user=Depends(get_user)):
    cursor = category_collection.find({})
    categories = []
    for category in cursor:
        category["_id"] = str(category["_id"])
        if category["parent_category"]:
            parent_category = db.dereference(category["parent_category"])
            if parent_category:
                parent_category["_id"] = str(parent_category["_id"])
                parent_category["image"] = image_dereference(parent_category["image"])
            category["parent_category"] = parent_category
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


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_category(id: str, data: Category, user=Depends(get_user)):
    if data.parent_id:
        parent_category = DBRef("categories", ObjectId(data.parent_id), "ecommerce")
    else:
        parent_category = None
    image = DBRef("images", ObjectId(data.image_id), "ecommerce")
    category = category_collection.update_one(
        {"_id": ObjectId(id.strip())},
        {
            "$set": {
                "name": data.name,
                "parent_category": parent_category,
                "image": image,
            }
        },
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
