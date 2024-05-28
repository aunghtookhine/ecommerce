from pydantic import BaseModel


class Product(BaseModel):
    name: str
    category_id: str
    description: str
    item: int
    feature_product: bool = False
    price: int
    img_ids: list[str]
