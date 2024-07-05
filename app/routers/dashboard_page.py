from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from ..routers.category import find_categories, find_category
from ..routers.product import find_products, find_product
from ..routers.image import find_images
from ..routers.checkout import find_checkouts, find_checkout
from ..routers.auth import find_users
from ..models.auth import check_is_logged_in, decode_token

templates = Jinja2Templates(directory="app/templates")


router = APIRouter()


@router.get("")
def redirect_route():
    return RedirectResponse("/dashboard/checkouts")


@router.get("/checkouts")
def checkout_page(request: Request, result: dict = Depends(check_is_logged_in)):
    if not result["is_logged_in"]:
        return RedirectResponse(result["redirect_url"])
    if not result["is_admin"]:
        return RedirectResponse("/")
    checkouts = find_checkouts(request)
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/checkouts.html",
        {
            "request": request,
            "token": token,
            "checkouts": checkouts,
            "username": result["username"],
        },
    )


@router.get("/checkouts/{id}")
def checkout_detail_page(
    request: Request, id: str, result: dict = Depends(check_is_logged_in)
):
    if not result["is_logged_in"]:
        return RedirectResponse(result["redirect_url"])
    if not result["is_admin"]:
        return RedirectResponse("/")
    checkout = find_checkout(id)
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/checkout.html",
        {
            "request": request,
            "token": token,
            "checkout": checkout,
            "username": result["username"],
        },
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
            "username": result["username"],
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
            "username": result["username"],
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
            "username": result["username"],
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
            "username": result["username"],
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
            "username": result["username"],
        },
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
            "username": result["username"],
        },
    )


@router.get("/change-password")
def change_password(request: Request, result: dict = Depends(check_is_logged_in)):
    if not result["is_logged_in"]:
        return RedirectResponse(result["redirect_url"])
    if not result["is_admin"]:
        return RedirectResponse("/")
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/change_password.html",
        {
            "request": request,
            "token": token,
            "username": result["username"],
            "email": result["email"],
        },
    )
