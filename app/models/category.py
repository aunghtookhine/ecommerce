from pydantic import BaseModel, field_validator
from fastapi import HTTPException, status


class Category(BaseModel):
    name: str
    parent_category: str = "asdfghjkl"
    img_id: str

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
