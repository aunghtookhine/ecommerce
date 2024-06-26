from pydantic import BaseModel, field_validator
from fastapi import HTTPException, status, Form
from ..db.mongodb import db
from ..models.category import category_dereference
from ..models.image import image_dereference


class Product(BaseModel):
    name: str
    category: str
    description: str
    item: int
    feature_product: bool = False
    price: int
    images: list[str]

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
    
    @classmethod
    def to_form_data(cls, name: str = Form(...), category: str = Form(...), description: str = Form(...), item:int = Form(...), feature_product:bool = Form(default=False), price: int = Form(...), images: list[str] = Form(default=[])):
        return cls(name=name, category=category, description=description, item=item, feature_product=feature_product, price=price, images=images)


def product_dereference(product_dbref):
    product = db.dereference(product_dbref)
    product["_id"] = str(product["_id"])
    product["category"] = category_dereference(product["category"])
    images = []
    for image in product["images"]:
        image = image_dereference(image)
        images.append(image)
    product["images"] = images
    return product
