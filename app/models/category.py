from pydantic import BaseModel, field_validator
from fastapi import HTTPException, status
from ..db.mongodb import db
from ..models.image import image_dereference


class Category(BaseModel):
    name: str
    parent_category: str = None
    image: str

    @field_validator("*")
    def str_strip(cls, value):
        return value.strip()

    @field_validator("*")
    def not_empty(cls, value):
        if not value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Fields cannot be empty",
            )
        return value


def category_dereference(category_dbref):
    category = db.dereference(category_dbref)
    if category:
        category["_id"] = str(category["_id"])
        if category["parent_category"]:
            category["parent_category"] = category_dereference(
                category["parent_category"]
            )
        category["image"] = image_dereference(category["image"])
    return category
