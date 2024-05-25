from fastapi import FastAPI
from .routers import auth, category, product

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(category.router, prefix="/categories", tags=["category"])
app.include_router(product.router, prefix="/products", tags=["product"])
