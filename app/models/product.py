from pydantic import BaseModel, field_validator
from fastapi import HTTPException, status


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
