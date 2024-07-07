from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from .product import find_product, find_products, find_feature_products
from .cart import get_cart_items
from .checkout import find_checkout, find_checkouts
from ..models.category import get_category_names
from fastapi.templating import Jinja2Templates
from ..models.auth import check_is_logged_in, decode_token


templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/")
def root(request: Request):
    products = find_products()
    feature_products = find_feature_products()
    token = request.session.get("token")
    payload = {}
    if token:
        payload = decode_token(token)
    cart_items = get_cart_items(request)
    total_qty = 0
    for qty in cart_items.values():
        total_qty += qty
    return templates.TemplateResponse(
        "website/index.html",
        {
            "request": request,
            "products": products,
            "total_qty": total_qty,
            "token": token,
            "username": payload.get("username"),
            "feature_products": feature_products
        },
    )


@router.get("/products/{product_id}")
def product_detail_page(request: Request, product_id: str):
    product = find_product(product_id)
    cart_items = get_cart_items(request)
    total_qty = 0
    for qty in cart_items.values():
        total_qty += qty
    categories = get_category_names(product["category"])
    token = request.session.get("token")
    payload = {}
    if token:
        payload = decode_token(token)
    return templates.TemplateResponse(
        "website/product_detail.html",
        {
            "request": request,
            "product": product,
            "total_qty": total_qty,
            "categories": categories,
            "token": token,
            "username": payload.get("username"),
        },
    )


@router.get("/cart")
def cart_page(
    request: Request,
):
    cart_items = get_cart_items(request)
    total = 0
    products = []
    for item, qty in cart_items.items():
        product = find_product(item)
        product["qty"] = qty
        total += product["price"] * product["qty"]
        products.append(product)
    token = request.session.get("token")
    payload = {}
    if token:
        payload = decode_token(token)
    return templates.TemplateResponse(
        "website/cart.html",
        {
            "request": request,
            "products": products,
            "total": total,
            "token": token,
            "username": payload.get("username"),
        },
    )


@router.get("/checkouts")
def checkout_page(request: Request, result: dict = Depends(check_is_logged_in)):
    if not result["is_logged_in"]:
        return RedirectResponse(result["redirect_url"])
    if result["is_admin"]:
        return RedirectResponse("/dashboard")
    checkouts = find_checkouts(request)
    cart_items = get_cart_items(request)
    total_qty = 0
    for qty in cart_items.values():
        total_qty += qty
    token = request.session.get("token")
    payload = {}
    if token:
        payload = decode_token(token)
    return templates.TemplateResponse(
        "website/checkout.html",
        {
            "request": request,
            "checkouts": checkouts,
            "total_qty": total_qty,
            "token": token,
            "username": payload.get("username"),
        },
    )


# @router.get("/change-password")
# def change_password_page(request: Request, result: dict = Depends(check_is_logged_in)):
#     token = request.session.get("token")
#     cart_items = get_cart_items(request)
#     total_qty = 0
#     for qty in cart_items.values():
#         total_qty += qty

#     return templates.TemplateResponse(
#         "website/change_password.html",
#         {"request": request, "token": token, "total_qty": total_qty},
#     )


@router.get("/pdf/{checkout_id}")
def pdf(request: Request, checkout_id: str, result: dict = Depends(check_is_logged_in)):
    if not result["is_logged_in"]:
        return RedirectResponse(result["redirect_url"])
    checkout = find_checkout(checkout_id)
    return templates.TemplateResponse(
        "website/pdf.html", {"request": request, "checkout": checkout}
    )
