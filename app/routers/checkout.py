from fastapi import APIRouter, Depends, HTTPException, status, Request
from ..models.auth import get_user, user_dereference, decode_token
from ..models.checkout import Checkout
from ..models.product import product_dereference
from ..db.mongodb import product_collection, checkout_collection, user_collection
from bson import ObjectId, DBRef

router = APIRouter()


@router.post("/")
def create_checkout(request: Request, user=Depends(get_user)):
    try:
        user_dbref = DBRef("users", ObjectId(user["_id"]), "ecommerce")
        session = request.session
        cart = session.get("cart")
        detail = []
        total = 0
        for product_id, quantity in cart.items():
            product = product_collection.find_one({"_id": ObjectId(product_id)})
            total += product["price"] * quantity
            product_dbref = DBRef("products", ObjectId(product_id), "ecommerce")
            detail.append({"product": product_dbref, "quantity": quantity})
        checkout = checkout_collection.insert_one(
            {"user": user_dbref, "detail": detail, "total": total}
        )
        if not checkout.inserted_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        session.pop("cart")
        return {"detail": "Successfully Ordered.", "success": True}
    except HTTPException as e:
        return {"detail": e.detail, "success": False}


@router.get("/")
def find_checkouts(request: Request, user=Depends(get_user)):
    session = request.session
    token = session.get("token")
    payload = decode_token(token)
    user = user_collection.find_one({"_id": ObjectId(payload["_id"])})
    user_dbref = DBRef("users", ObjectId(payload["_id"]), "ecommerce")
    cursor = checkout_collection.find({"user": user_dbref})
    if user["is_admin"]:
        cursor = checkout_collection.find({})
    checkouts = []
    for checkout in cursor:
        detail = []
        checkout["_id"] = str(checkout["_id"])
        checkout["user"] = user_dereference(checkout["user"])
        for product_detail in checkout["detail"]:
            product_detail["product"] = product_dereference(product_detail["product"])
            detail.append(product_detail)
        checkouts.append(checkout)
    return checkouts


@router.get("/{checkout_id}")
def find_checkout(checkout_id: str, user=Depends(get_user)):
    checkout = checkout_collection.find_one({"_id": ObjectId(checkout_id)})
    if not checkout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Checkout ID"
        )
    checkout["_id"] = str(checkout["_id"])
    checkout["user"] = user_dereference(checkout["user"])
    detail = []
    for product_detail in checkout["detail"]:
        product_detail["product"] = product_dereference(product_detail["product"])
        detail.append(product_detail)
    checkout["detail"] = detail
    return checkout
