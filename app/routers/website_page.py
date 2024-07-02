from fastapi import APIRouter, Request
from .product import find_product, find_products
from .cart import get_cart_items
from .checkout import find_checkout, find_checkouts
from ..models.category import get_category_names
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/")
def root(request: Request):
    products = find_products()
    cart_items = get_cart_items(request)
    total_qty = 0
    for qty in cart_items.values():
        total_qty += qty
    return templates.TemplateResponse(
        "website/index.html",
        {"request": request, "products": products, "total_qty": total_qty},
    )


@router.get("/products/{product_id}")
def product_detail_page(request: Request, product_id: str):
    product = find_product(product_id)
    cart_items = get_cart_items(request)
    total_qty = 0
    for qty in cart_items.values():
        total_qty += qty

    categories = get_category_names(product["category"])

    return templates.TemplateResponse(
        "website/product_detail.html",
        {
            "request": request,
            "product": product,
            "total_qty": total_qty,
            "categories": categories,
        },
    )


@router.get("/pdf/{checkout_id}")
def pdf(request: Request, checkout_id: str):
    checkout = find_checkout(checkout_id)
    return templates.TemplateResponse(
        "website/pdf.html", {"request": request, "checkout": checkout}
    )


@router.get("/cart")
def cart_page(request: Request):
    cart_items = get_cart_items(request)
    total = 0
    products = []
    for item, qty in cart_items.items():
        product = find_product(item)
        product["qty"] = qty
        total += product["price"] * product["qty"]
        products.append(product)
    message = get_message(request)
    return templates.TemplateResponse(
        "website/cart.html",
        {"request": request, "products": products, "total": total, "message": message},
    )


@router.get("/checkout")
def checkout_page(request: Request):
    checkouts = find_checkouts(request)
    cart_items = get_cart_items(request)
    total_qty = 0
    for qty in cart_items.values():
        total_qty += qty
    return templates.TemplateResponse(
        "website/checkout.html",
        {"request": request, "checkouts": checkouts, "total_qty": total_qty},
    )


@router.get("/api/message")
def get_message(request: Request):
    session = request.session
    message = session.get("message")
    return {"message": message}
