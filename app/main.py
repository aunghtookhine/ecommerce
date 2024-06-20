from fastapi import FastAPI, Request, Depends

from .routers import auth, category, product, image, checkout
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .models.auth import get_user
from .routers.category import find_categories


templates = Jinja2Templates(directory="app/templates")
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(category.router, prefix="/api/categories", tags=["category"])
app.include_router(product.router, prefix="/api/products", tags=["product"])
app.include_router(image.router, prefix="/api/images", tags=["image"])
app.include_router(checkout.router, prefix="/api/checkouts", tags=["checkout"])


@app.get("/dashboard")
def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/dashboard/categories")
def category_page(request: Request):
    categories = find_categories()
    return templates.TemplateResponse(
        "categories.html", {"request": request, "categories": categories}
    )


@app.get("/dashboard/products")
def product_page(request: Request):
    return templates.TemplateResponse("products.html", {"request": request})


@app.get("/dashboard/users")
def user_page(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})


@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
def login(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# generate json file for api
import json, dotenv, os

dotenv.load_dotenv(override=True)
filename = os.getenv("API_JSON_FILENAME")

json_data = app.openapi()
with open(filename, "w") as json_file:
    json.dump(json_data, json_file)
