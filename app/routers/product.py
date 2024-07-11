from fastapi import APIRouter, HTTPException, status, Depends, Form, Request
from ..models.product import Product, filter_products_by_category
from ..db.mongodb import product_collection
from bson import ObjectId, DBRef
from ..models.auth import get_user, check_authorization
from ..models.category import category_dereference
from ..models.image import image_dereference
from dotenv import load_dotenv
import os
import math

load_dotenv(override=True)
router = APIRouter()

PAGE_SIZE = 10


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(
    request: Request,
    data: Product,
    user=Depends(get_user),
    check_auth=Depends(check_authorization),
):
    try:
        product_dict = data.model_dump()
        if product_dict["category"] != "null":
            product_dict["category"] = DBRef(
                "categories",
                ObjectId(product_dict["category"]),
                os.getenv("DATABASE_NAME"),
            )
        else:
            product_dict["category"] = None
        images = []
        if product_dict["images"]:
            for image in product_dict["images"]:
                images.append(
                    DBRef("images", ObjectId(image), os.getenv("DATABASE_NAME"))
                )
        product_dict["images"] = images
        product = product_collection.insert_one(product_dict)
        if product.inserted_id:
            return {"detail": "Successfully Created.", "success": True}
    except Exception as e:
        return {"detail": "Something Went Wrong.", "success": False}


@router.get("/feature", status_code=status.HTTP_200_OK)
def find_feature_products(user=Depends(get_user)):
    cursor = product_collection.find({"feature_product": True})
    products = []
    for product in cursor:
        product["_id"] = str(product["_id"])
        product["category"] = category_dereference(product["category"])
        images = []
        for image_id in product["images"]:
            image = image_dereference(image_id)
            if image:
                images.append(image)
        product["images"] = images
        products.append(product)
    return products


@router.get("/", status_code=status.HTTP_200_OK)
def find_products(request: Request, user=Depends(get_user)):
    q = request.query_params.get("q")
    category = request.query_params.get("category")
    page = request.query_params.get("page")
    if not page:
        page = 1
    skip = (int(page) - 1) * PAGE_SIZE
    if q != None:
        cursor = (
            product_collection.find({"name": {"$regex": q, "$options": "i"}})
            .skip(skip)
            .limit(PAGE_SIZE)
        )
        count = product_collection.count_documents(
            {"name": {"$regex": q, "$options": "i"}}
        )
    else:
        if str(request.url_for("products_page")) in str(request.url):
            cursor = product_collection.find({})
            count = product_collection.count_documents({})
        else:
            cursor = product_collection.find({}).skip(skip).limit(PAGE_SIZE)
            count = product_collection.count_documents({})

    pages = math.ceil(count / PAGE_SIZE)
    products = []
    for product in cursor:
        product["_id"] = str(product["_id"])
        product["category"] = category_dereference(product["category"])
        images = []
        for image_id in product["images"]:
            image = image_dereference(image_id)
            if image:
                images.append(image)
        product["images"] = images
        products.append(product)
    if category:
        products = filter_products_by_category(products, category)
    return {"products": products, "pages": pages}


@router.get("/{id}", status_code=status.HTTP_200_OK)
def find_product(id: str, user=Depends(get_user)):
    product = product_collection.find_one({"_id": ObjectId(id.strip())})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Category Id."
        )
    product["_id"] = str(product["_id"])
    product["category"] = category_dereference(product["category"])
    images = []
    for image_id in product["images"]:
        image = image_dereference(image_id)
        if image:
            images.append(image)
    product["images"] = images
    return product


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_product(
    id: str,
    data: Product,
    user=Depends(get_user),
    check_auth=Depends(check_authorization),
):
    try:
        data_dict = data.model_dump()
        data_dict["category"] = DBRef(
            "categories", ObjectId(data_dict["category"]), os.getenv("DATABASE_NAME")
        )
        images = []
        for image in data_dict["images"]:
            image = DBRef("images", ObjectId(image), os.getenv("DATABASE_NAME"))
            images.append(image)
        data_dict["images"] = images
        product = product_collection.find_one_and_update(
            {"_id": ObjectId(id.strip())}, {"$set": data_dict}
        )
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Product Id."
            )
        return {"detail": "Successfully Updated.", "success": True}
    except HTTPException as e:
        return {"detail": e.detail, "success": False}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    id: str, user=Depends(get_user), check_auth=Depends(check_authorization)
):
    try:
        product = product_collection.find_one_and_delete({"_id": ObjectId(id.strip())})
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Product Id."
            )
        return {"detail": "Successfully Deleted.", "success": True}
    except HTTPException as e:
        return {"detail": e.detail, "success": False}


@router.patch("/{id}", status_code=status.HTTP_200_OK)
def update_stock(id: str, data: int, user=Depends(get_user)):
    result = product_collection.find_one_and_update(
        {"_id": ObjectId(id.strip())}, {"$inc": {"item": data}}
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Product Id."
        )
    return {"detail": "Successfully Updated Stock"}
