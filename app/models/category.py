from pydantic import BaseModel
from fastapi import Path, Query


class Category(BaseModel):
    name: str
    parent_category: int = 0
    img_id: int
