from fastapi import APIRouter, status, HTTPException
from ..models.category import Category
from ..db.mongodb import category_collection

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_category(data: Category):
    category_dict = data.model_dump()
    category_collection.insert_one(category_dict)


@router.get("/{id}", status_code=status.HTTP_200_OK)
def find_category(id):
    category = category_collection.find_one({"_id": id})
    print(category)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Category Id"
        )
    return category
