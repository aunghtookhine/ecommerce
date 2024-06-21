from pydantic import BaseModel


class Cart(BaseModel):
    product_id: str
    qty: int


class AdjustQty(BaseModel):
    product_id: str
