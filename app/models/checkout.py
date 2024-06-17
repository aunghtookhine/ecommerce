from pydantic import BaseModel


class Checkout(BaseModel):
    product: str
