from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from ..routers.category import find_categories, find_category
from ..routers.product import find_products, find_product
from ..routers.image import find_images
from ..routers.checkout import find_checkouts, find_checkout
from ..routers.auth import find_users, find_user
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
    checkouts_dict = find_checkouts(request)
    checkouts, pages = checkouts_dict.values()
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/checkouts.html",
        {
            "request": request,
            "token": token,
            "checkouts": checkouts,
            "username": result["username"],
            "pages": pages,
            "checkouts": checkouts,
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
    categories_dict = find_categories(request)
    categories, page_categories, pages = categories_dict.values()
    images = find_images(request)
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/categories.html",
        {
            "request": request,
            "categories": categories,
            "page_categories": page_categories,
            "images": images,
            "token": token,
            "pages": pages,
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
    categories_dict = find_categories(request)
    categories = categories_dict["categories"]
    images = find_images(request)
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
    products_dict = find_products(request)
    products, pages = products_dict.values()
    categories = find_categories(request)
    images = find_images(request)
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/products.html",
        {
            "request": request,
            "products": products,
            "categories": categories,
            "categories": categories,
            "images": images,
            "token": token,
            "username": result["username"],
            "pages": pages,
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
    images = find_images(request)
    image_ids = []
    for image in product["images"]:
        image_ids.append(image["_id"])
    categories = find_categories(request)
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
            "categories": categories,
        },
    )


@router.get("/images")
def image_page(request: Request, result: dict = Depends(check_is_logged_in)):
    if not result["is_logged_in"]:
        return RedirectResponse(result["redirect_url"])
    if not result["is_admin"]:
        return RedirectResponse("/")
    images = find_images(request)
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/images.html",
        {
            "request": request,
            "images": images,
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
    users_dict = find_users(request)
    users, pages = users_dict.values()
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/users.html",
        {
            "request": request,
            "users": users,
            "pages": pages,
            "token": token,
            "username": result["username"],
        },
    )


@router.get("/users/{id}")
def user_detail_page(
    request: Request,
    id: str,
    result: dict = Depends(check_is_logged_in),
):
    if not result["is_logged_in"]:
        return RedirectResponse(result["redirect_url"])
    if not result["is_admin"]:
        return RedirectResponse("/")
    user = find_user(id)
    token = request.session.get("token")
    return templates.TemplateResponse(
        "dashboard/edit_user.html",
        {
            "request": request,
            "user": user,
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
        },
    )
