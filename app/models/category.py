from pydantic import BaseModel, field_validator
from fastapi import HTTPException, status, Form
from ..db.mongodb import db
from ..models.image import image_dereference


class Category(BaseModel):
    name: str
    parent_category: str = None
    image: str = None

    @field_validator("*")
    def str_strip(cls, value):
        return value.strip()

    @field_validator("name")
    def not_empty(cls, value):
        if not value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Fields cannot be empty",
            )
        return value

    @classmethod
    def to_form_data(
        cls,
        name: str = Form(...),
        parent_category: str = Form(...),
        image: str = Form(...),
    ):
        return cls(name=name, parent_category=parent_category, image=image)


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


def get_category_names(category):
    names = []

    def retrieve_name(category):
        if category and category["name"]:
            names.append(category["name"])
        if category and category["parent_category"]:
            retrieve_name(category["parent_category"])

    retrieve_name(category)
    reverse_names = names[::-1]
    return " > ".join(reverse_names)
