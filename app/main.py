from fastapi import FastAPI
from .routers import user, category

app = FastAPI()

app.include_router(user.router, prefix="/auth", tags=["auth"])
app.include_router(category.router, prefix="/categories", tags=["category"])
