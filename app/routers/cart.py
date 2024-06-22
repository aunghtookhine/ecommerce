from fastapi import APIRouter, Depends, HTTPException, status, Request
from ..models.cart import Cart, AdjustQty
from ..models.auth import get_user
from ..db.mongodb import product_collection
from bson import ObjectId
from ..routers.product import find_product, update_stock
from pymongo import UpdateOne

router = APIRouter()


@router.post("/")
def add_to_cart(data: Cart, request: Request, user=Depends(get_user)):
    data_dict = data.model_dump()
    product = product_collection.find_one({"_id": ObjectId(data_dict["product_id"])})
    if product["item"] < 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Insufficient stock"
        )
    product["item"] -= 1
    update_stock(data_dict["product_id"], -1)
    session = request.session
    cart_items = session.get("cart", {})
    if data_dict["product_id"] in cart_items:
        cart_items[data_dict["product_id"]] += data_dict["qty"]
    else:
        cart_items[data_dict["product_id"]] = data_dict["qty"]
    session["cart"] = cart_items
    return {"detail": "Successfully added.", "success": True}


@router.get("/")
def get_cart_items(request: Request, user=Depends(get_user)):
    session = request.session
    cart_items = session.get("cart", {})
    return cart_items


@router.post("/increase")
def increase_qty(data: AdjustQty, request: Request, user=Depends(get_user)):
    data_dict = data.model_dump()
    cart_items = get_cart_items(request)
    product = find_product(data_dict["product_id"])
    if product["item"] < 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Insufficient Stock"
        )
    product["item"] -= 1
    update_stock(data_dict["product_id"], -1)
    cart_items[data_dict["product_id"]] += 1
    request.session["cart"] = cart_items
    return {"detail": "Successfully added.", "success": True}


@router.post("/decrease")
def decrease_qty(data: AdjustQty, request: Request, user=Depends(get_user)):
    data_dict = data.model_dump()
    cart_items = get_cart_items(request)
    if cart_items[data_dict["product_id"]] == 1:
        del cart_items[data_dict["product_id"]]
    else:
        cart_items[data_dict["product_id"]] -= 1
    update_stock(data_dict["product_id"], 1)
    request.session["cart"] = cart_items
    return {"detail": "Successfully removed.", "success": True}


@router.get("/clear")
def clear_session(request: Request, user=Depends(get_user)):
    session = request.session
    cart_items = session.get("cart")
    operations = []
    for product_id, qty in cart_items.items():
        operations.append(
            UpdateOne({"_id": ObjectId(product_id)}, {"$inc": {"item": qty}})
        )
    result = product_collection.bulk_write(operations)
    if not result.bulk_api_result.get("writeErrors"):
        session.pop("cart", None)
        return {"detail": "Successfully Cleared"}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
