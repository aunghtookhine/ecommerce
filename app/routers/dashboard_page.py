from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from ..routers.category import find_categories

templates = Jinja2Templates(directory="app/templates")


router = APIRouter()


@router.get("/dashboard")
def home_page(request: Request):
    return templates.TemplateResponse("dashboard/home.html", {"request": request})


@router.get("/dashboard/categories")
def category_page(request: Request):
    categories = find_categories()
    return templates.TemplateResponse(
        "dashboard/categories.html", {"request": request, "categories": categories}
    )


@router.get("/dashboard/products")
def product_page(request: Request):
    return templates.TemplateResponse("dashboard/products.html", {"request": request})


@router.get("/dashboard/users")
def user_page(request: Request):
    return templates.TemplateResponse("dashboard/users.html", {"request": request})
