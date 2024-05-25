from fastapi import FastAPI
from .routers import user, category, product

app = FastAPI()

app.include_router(user.router, prefix="/auth", tags=["auth"])
app.include_router(category.router, prefix="/categories", tags=["category"])
app.include_router(product.router, prefix="/products", tags=["product"])
