from fastapi import FastAPI, Request, Depends
from .routers import (
    auth,
    category,
    product,
    image,
    checkout,
    cart,
    website_page,
    dashboard_page,
)
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
from .models.auth import check_is_logged_in
from fastapi_pagination.ext.pymongo import paginate
from fastapi_pagination import add_pagination

from dotenv import load_dotenv
import os

load_dotenv(override=True)

templates = Jinja2Templates(directory="app/templates")
app = FastAPI()
add_pagination(app)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(category.router, prefix="/api/categories", tags=["category"])
app.include_router(product.router, prefix="/api/products", tags=["product"])
app.include_router(image.router, prefix="/api/images", tags=["image"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(checkout.router, prefix="/api/checkouts", tags=["checkout"])
app.include_router(website_page.router, tags=["website"])
app.include_router(dashboard_page.router, prefix="/dashboard", tags=["dashboard"])


@app.get("/login")
def login(request: Request, result: dict = Depends(check_is_logged_in)):
    if result["is_logged_in"]:
        if not result["is_admin"]:
            return RedirectResponse("/")
        else:
            return RedirectResponse("/dashboard")
    return templates.TemplateResponse("layout/login.html", {"request": request})


@app.get("/register")
def register(request: Request, result: dict = Depends(check_is_logged_in)):
    if result["is_logged_in"]:
        if not result["is_admin"]:
            return RedirectResponse("/")
        else:
            return RedirectResponse("/dashboard")
    return templates.TemplateResponse("layout/register.html", {"request": request})


# generate json file for api
import json, dotenv, os

dotenv.load_dotenv(override=True)
filename = os.getenv("API_JSON_FILENAME")

json_data = app.openapi()
with open(filename, "w") as json_file:
    json.dump(json_data, json_file)
