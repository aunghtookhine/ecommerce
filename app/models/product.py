from pydantic import BaseModel


class Product(BaseModel):
    name: str
    category_id: int
    description: str
    feature_product: bool = False
    price: int
    img_ids: list[int]
