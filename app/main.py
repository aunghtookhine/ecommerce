from fastapi import FastAPI, Request
from .routers import auth, category, product
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse


templates = Jinja2Templates(directory="app/templates")
app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(category.router, prefix="/categories", tags=["category"])
app.include_router(product.router, prefix="/products", tags=["product"])


@app.get("/")
def root():
    return RedirectResponse("/login")


@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
def login(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
