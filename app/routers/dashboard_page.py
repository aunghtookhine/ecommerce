from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from ..routers.category import find_categories, find_category
from ..routers.product import find_products, find_product
from ..routers.image import find_images
from ..db.mongodb import user_collection
from bson import ObjectId
from ..models.auth import check_logged_in

templates = Jinja2Templates(directory="app/templates")


router = APIRouter()


@router.get("/")
def home_page(request: Request, is_logged_in: bool = Depends(check_logged_in)):
    if not is_logged_in:
        return RedirectResponse("/login")
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/home.html", {"request": request, "token": token}
    )


@router.get("/categories")
def category_page(request: Request, is_logged_in: bool = Depends(check_logged_in)):
    if not is_logged_in:
        return RedirectResponse("/login")
    categories = find_categories()
    return templates.TemplateResponse(
        "dashboard/categories.html", {"request": request, "categories": categories}
    )


@router.get("/categories/create")
def create_category_page(
    request: Request, is_logged_in: bool = Depends(check_logged_in)
):
    if not is_logged_in:
        return RedirectResponse("/login")
    categories = find_categories()
    images = find_images()
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/create_category.html",
        {
            "request": request,
            "categories": categories,
            "images": images,
            "token": token,
        },
    )


@router.get("/categories/{id}")
def category_detail_page(
    request: Request, id: str, is_logged_in: bool = Depends(check_logged_in)
):
    if not is_logged_in:
        return RedirectResponse("/login")
    category = find_category(id)
    categories = find_categories()
    images = find_images()
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/edit_category.html",
        {
            "request": request,
            "category": category,
            "categories": categories,
            "images": images,
            "token": token,
        },
    )


@router.get("/products")
def product_page(request: Request, is_logged_in: bool = Depends(check_logged_in)):
    if not is_logged_in:
        return RedirectResponse("/login")
    products = find_products()
    return templates.TemplateResponse(
        "dashboard/products.html", {"request": request, "products": products}
    )


@router.get("/products/create")
def create_product_page(
    request: Request, is_logged_in: bool = Depends(check_logged_in)
):
    if not is_logged_in:
        return RedirectResponse("/login")
    categories = find_categories()
    return templates.TemplateResponse(
        "dashboard/create_product.html", {"request": request, "categories": categories}
    )


@router.get("/products/{id}")
def product_detail_page(
    request: Request, id: str, is_logged_in: bool = Depends(check_logged_in)
):
    if not is_logged_in:
        return RedirectResponse("/login")
    product = find_product(id)
    categories = find_categories()
    return templates.TemplateResponse(
        "dashboard/edit_product.html",
        {"request": request, "product": product, "categories": categories},
    )


@router.get("/images")
def image_page(request: Request, is_logged_in: bool = Depends(check_logged_in)):
    if not is_logged_in:
        return RedirectResponse("/login")
    images = find_images()
    categories = find_categories()
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/images.html",
        {
            "request": request,
            "images": images,
            "categories": categories,
            "token": token,
        },
    )


@router.get("/images/create")
def create_image_page(request: Request, is_logged_in: bool = Depends(check_logged_in)):
    if not is_logged_in:
        return RedirectResponse("/login")
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/create_image.html", {"request": request, "token": token}
    )


@router.get("/users")
def user_page(request: Request, is_logged_in: bool = Depends(check_logged_in)):
    if not is_logged_in:
        return RedirectResponse("/login")
    return templates.TemplateResponse("dashboard/users.html", {"request": request})
