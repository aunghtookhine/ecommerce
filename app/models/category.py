from pydantic import BaseModel
from fastapi import Path, Query


class Category(BaseModel):
    name: str
    parent_category: str = "0"
    img_id: str
