from pydantic import BaseModel, field_validator
from fastapi import HTTPException, status, Form
from ..db.mongodb import db
from ..models.category import category_dereference
from ..models.image import image_dereference


class Product(BaseModel):
    name: str
    category: str
    description: str
    item: int = 0
    feature_product: bool = False
    price: int = 0
    images: list[str] = []

    @field_validator("*")
    def str_strip(cls, value):
        if type(value) == str:
            return value.strip()
        return value

    @field_validator("name", "description")
    def not_empty(cls, value):
        if not value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Fields cannot be empty",
            )
        return value


def product_dereference(product_dbref):
    product = db.dereference(product_dbref)
    if product:
        product["_id"] = str(product["_id"])
        product["category"] = category_dereference(product["category"])
        images = []
        for image in product["images"]:
            image = image_dereference(image)
            images.append(image)
        product["images"] = images
    return product


def filter_products_by_category(products, category_id):
    new_products = []

    def check_category(category):
        if category and category["_id"] == category_id:
            return True
        if category and category["parent_category"]:
            return check_category(category["parent_category"])
        return False

    for product in products:
        if check_category(product["category"]):
            new_products.append(product)

    return new_products
