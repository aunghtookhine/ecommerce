from fastapi import APIRouter, Depends, HTTPException, status, Request
from ..models.cart import Cart, AdjustQty
from ..models.auth import get_user
from ..db.mongodb import product_collection
from bson import ObjectId

router = APIRouter()


@router.post("/")
def add_to_cart(data: Cart, request: Request, user=Depends(get_user)):
    data_dict = data.model_dump()
    product = product_collection.find_one({"_id": ObjectId(data_dict["product_id"])})
    if data_dict["qty"] > product["item"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Insufficient stock"
        )
    session = request.session
    user_cart = session.get("cart", {})
    if data_dict["product_id"] in user_cart:
        user_cart[data_dict["product_id"]] += data_dict["qty"]
    else:
        user_cart[data_dict["product_id"]] = data_dict["qty"]
    session["cart"] = user_cart
    return {"detail": "Success", "session": session["cart"]}


@router.get("/")
def get_cart_items(request: Request, user=Depends(get_user)):
    session = request.session
    cart_items = session.get("cart", {})
    return cart_items


@router.post("/increase")
def increase_qty(data: AdjustQty, request: Request, user=Depends(get_user)):
    data_dict = data.model_dump()
    cart_items = get_cart_items(request)
    cart_items[data_dict["product_id"]] += 1
    request.session["cart"] = cart_items
    return {"detail": "Successfully Increased"}


@router.post("/decrease")
def decrease_qty(data: AdjustQty, request: Request, user=Depends(get_user)):
    data_dict = data.model_dump()
    cart_items = get_cart_items(request)
    if cart_items[data_dict["product_id"]] == 1:
        del cart_items[data_dict["product_id"]]
    else:
        cart_items[data_dict["product_id"]] -= 1
    request.session["cart"] = cart_items
    return {"detail": "Successfully Decreased"}
