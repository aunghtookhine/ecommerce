from fastapi import FastAPI, Request, Depends
from .routers import auth, category, product, image, checkout, cart
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .models.auth import get_user
from .routers.category import find_categories
from .routers.product import find_products, find_product
from .routers.cart import get_cart_items
from starlette.middleware.sessions import SessionMiddleware
from fastapi.security import HTTPBearer


templates = Jinja2Templates(directory="app/templates")
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(SessionMiddleware, secret_key="ecommerce")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(category.router, prefix="/api/categories", tags=["category"])
app.include_router(product.router, prefix="/api/products", tags=["product"])
app.include_router(image.router, prefix="/api/images", tags=["image"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(checkout.router, prefix="/api/checkouts", tags=["checkout"])

bearer_scheme = HTTPBearer()


@app.get("/")
def root(request: Request):
    products = find_products()
    cart_items = get_cart_items(request)
    total_qty = 0
    for qty in cart_items.values():
        total_qty += qty
    return templates.TemplateResponse(
        "index.html", {"request": request, "products": products, "total_qty": total_qty}
    )


@app.get("/cart")
def cart_page(request: Request):
    cart_items = get_cart_items(request)
    total = 0
    products = []
    for item, qty in cart_items.items():
        product = find_product(item)
        product["qty"] = qty
        total += product["price"] * product["qty"]
        products.append(product)

    return templates.TemplateResponse(
        "cart.html", {"request": request, "products": products, "total": total}
    )


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
