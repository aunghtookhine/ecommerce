from pydantic import BaseModel, field_validator
from fastapi import HTTPException, status


class Checkout(BaseModel):
    user_id: str
    product_id: str
    quantity: int = 1
    amount: int = 0


class UpdateCheckout(BaseModel):
    user_id: str
    product_id: str
