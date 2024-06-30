from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from ..routers.category import find_categories
from ..routers.product import find_products, find_product

templates = Jinja2Templates(directory="app/templates")


router = APIRouter()


@router.get("/")
def home_page(request: Request):
    return templates.TemplateResponse("dashboard/home.html", {"request": request})


@router.get("/categories")
def category_page(request: Request):
    categories = find_categories()
    return templates.TemplateResponse(
        "dashboard/categories.html", {"request": request, "categories": categories}
    )


@router.get("/products")
def product_page(request: Request):
    products = find_products()
    return templates.TemplateResponse("dashboard/products.html", {"request": request, 'products': products})

@router.get('/products/create')
def create_product_page(request: Request):
    categories = find_categories()
    return templates.TemplateResponse("dashboard/create_product.html", {"request": request, 'categories': categories})

@router.get('/products/{id}')
def product_detail_page(request: Request, id: str):
    product = find_product(id)
    return templates.TemplateResponse("dashboard/product.html", {"request": request, 'product': product})

@router.get("/users")
def user_page(request: Request):
    return templates.TemplateResponse("dashboard/users.html", {"request": request})
