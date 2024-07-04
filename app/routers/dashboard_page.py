from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from ..routers.category import find_categories, find_category
from ..routers.product import find_products, find_product
from ..routers.image import find_images
from ..routers.auth import find_users
from ..models.auth import check_is_logged_in

templates = Jinja2Templates(directory="app/templates")


router = APIRouter()


@router.get("")
def home_page(request: Request, result: dict = Depends(check_is_logged_in)):
    if not result["is_logged_in"]:
        return RedirectResponse(result["redirect_url"])
    if not result["is_admin"]:
        return RedirectResponse("/")
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/home.html", {"request": request, "token": token}
    )


@router.get("/categories")
def category_page(request: Request, result: dict = Depends(check_is_logged_in)):
    if not result["is_logged_in"]:
        return RedirectResponse(result["redirect_url"])
    if not result["is_admin"]:
        return RedirectResponse("/")
    categories = find_categories()
    images = find_images()
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/categories.html",
        {
            "request": request,
            "categories": categories,
            "images": images,
            "token": token,
        },
    )


@router.get("/categories/{id}")
def category_detail_page(
    request: Request, id: str, result: dict = Depends(check_is_logged_in)
):
    if not result["is_logged_in"]:
        return RedirectResponse(result["redirect_url"])
    if not result["is_admin"]:
        return RedirectResponse("/")
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
def product_page(request: Request, result: dict = Depends(check_is_logged_in)):
    if not result["is_logged_in"]:
        return RedirectResponse(result["redirect_url"])
    if not result["is_admin"]:
        return RedirectResponse("/")
    products = find_products()
    categories = find_categories()
    images = find_images()
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/products.html",
        {
            "request": request,
            "products": products,
            "categories": categories,
            "images": images,
            "token": token,
        },
    )


@router.get("/products/{id}")
def product_detail_page(
    request: Request, id: str, result: dict = Depends(check_is_logged_in)
):
    if not result["is_logged_in"]:
        return RedirectResponse(result["redirect_url"])
    if not result["is_admin"]:
        return RedirectResponse("/")
    product = find_product(id)
    images = find_images()
    image_ids = []
    for image in product["images"]:
        image_ids.append(image["_id"])
    categories = find_categories()
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/edit_product.html",
        {
            "request": request,
            "product": product,
            "categories": categories,
            "images": images,
            "image_ids": image_ids,
            "token": token,
        },
    )


@router.get("/images")
def image_page(request: Request, result: dict = Depends(check_is_logged_in)):
    if not result["is_logged_in"]:
        return RedirectResponse(result["redirect_url"])
    if not result["is_admin"]:
        return RedirectResponse("/")
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
def create_image_page(request: Request, result: dict = Depends(check_is_logged_in)):
    if not result["is_logged_in"]:
        return RedirectResponse(result["redirect_url"])
    if not result["is_admin"]:
        return RedirectResponse("/")
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/create_image.html", {"request": request, "token": token}
    )


@router.get("/users")
def user_page(request: Request, result: dict = Depends(check_is_logged_in)):
    if not result["is_logged_in"]:
        return RedirectResponse(result["redirect_url"])
    if not result["is_admin"]:
        return RedirectResponse("/")
    users = find_users()
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/users.html",
        {
            "request": request,
            "users": users,
            "token": token,
        },
    )
