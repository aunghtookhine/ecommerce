from pydantic import BaseModel
from fastapi import Path, Query


class Category(BaseModel):
    name: str
    parentCategory: int = 0
    imgId: int
