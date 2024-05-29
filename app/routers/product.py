from fastapi import APIRouter, HTTPException, status, Depends
from ..models.product import Product
from ..db.mongodb import product_collection
from bson import ObjectId
from ..utils.utils import dict_strip

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(data: Product):
    product_dict = data.model_dump()
    dict_strip(product_dict)
    product = product_collection.insert_one(product_dict)
    if not product.acknowledged:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    return {"_id": str(product.inserted_id)}


@router.get("/", status_code=status.HTTP_200_OK)
def find_products():
    cursor = product_collection.find({})
    products = []
    for product in cursor:
        product["_id"] = str(product["_id"])
        products.append(product)
    return products


@router.get("/{id}", status_code=status.HTTP_200_OK)
def find_product(id: str):
    product = product_collection.find_one({"_id": ObjectId(id)})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Category Id"
        )
    product["_id"] = str(product["_id"])
    return product


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_product(id: str, data: Product):
    product = product_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": data.model_dump()}
    )
    if not product.matched_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Product Id"
        )
    return {"msg": "Successfully Updated"}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id: str):
    product = product_collection.delete_one({"_id": ObjectId(id)})
    if not product.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Product Id"
        )
