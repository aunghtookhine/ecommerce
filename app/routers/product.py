from fastapi import APIRouter, HTTPException, status, Depends, Form, Request
from fastapi.responses import RedirectResponse
from ..models.product import Product
from ..db.mongodb import product_collection
from bson import ObjectId, DBRef
from ..models.auth import get_user
from ..models.category import category_dereference
from ..models.image import image_dereference

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(
    request: Request,
    data: Product = Depends(Product.to_form_data),
    token: str = Form(...),
):
    user = get_user(request, token)
    product_dict = data.model_dump()
    if product_dict["category"] != "null":
        product_dict["category"] = DBRef(
            "categories", ObjectId(product_dict["category"]), "ecommerce"
        )
    else:
        product_dict["category"] = None
    images = []
    if product_dict["images"]:
        for image in product_dict["images"]:
            images.append(DBRef("images", ObjectId(image), "ecommerce"))
    product_dict["images"] = images
    product = product_collection.insert_one(product_dict)
    if product.inserted_id:
        return RedirectResponse(
            "/dashboard/products", status_code=status.HTTP_302_FOUND
        )


@router.get("/", status_code=status.HTTP_200_OK)
def find_products(user=Depends(get_user)):
    cursor = product_collection.find({})
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


@router.get("/{id}", status_code=status.HTTP_200_OK)
def find_product(id: str, user=Depends(get_user)):
    product = product_collection.find_one({"_id": ObjectId(id.strip())})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Category Id"
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
def update_product(id: str, data: Product, user=Depends(get_user)):
    data_dict = data.model_dump()
    data_dict["category"] = DBRef(
        "categories", ObjectId(data_dict["category"]), "ecommerce"
    )
    images = []
    for image in data_dict["images"]:
        image = DBRef("images", ObjectId(image), "ecommerce")
        images.append(image)
    data_dict["images"] = images
    product = product_collection.find_one_and_update(
        {"_id": ObjectId(id.strip())}, {"$set": data_dict}
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Product Id"
        )
    return {"detail": "Successfully Updated"}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id: str, user=Depends(get_user)):
    product = product_collection.find_one_and_delete({"_id": ObjectId(id.strip())})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Product Id"
        )


@router.patch("/{id}", status_code=status.HTTP_200_OK)
def update_stock(id: str, data: int, user=Depends(get_user)):
    result = product_collection.find_one_and_update(
        {"_id": ObjectId(id.strip())}, {"$inc": {"item": data}}
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Product Id"
        )
    return {"detail": "Successfully Updated Stock"}
