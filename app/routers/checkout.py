from fastapi import APIRouter, status
from ..models.checkout import Checkout, UpdateCheckout
from ..db.mongodb import product_collection, user_collection, checkout_collection
from bson import ObjectId

router = APIRouter()


@router.post("/", status_code=status.HTTP_200_OK)
def checkout(data: Checkout):
    data_dict = data.model_dump()
    product = product_collection.find_one({"_id": ObjectId(data_dict["product_id"])})
    if product["item"] < data_dict["quantity"]:
        return {"detail": "Insufficient quantity"}
    product_collection.update_one(
        {"_id": ObjectId(data_dict["product_id"])},
        {"$set": {"item": product["item"] - data_dict["quantity"]}},
    )
    data_dict["amount"] = data_dict["amount"] + (
        data_dict["quantity"] * product["price"]
    )
    checkout = checkout_collection.find_one(
        {"user_id": data_dict["user_id"], "product_id": data_dict["product_id"]}
    )
    if not checkout:
        new_checkout = checkout_collection.insert_one(data_dict)
        if new_checkout.acknowledged:
            return {"detail": "Successfully Created"}

    total_quantity = data_dict["quantity"] + checkout["quantity"]
    total_amount = data_dict["amount"] + checkout["amount"]

    updated_checkout = checkout_collection.update_one(
        {"_id": checkout["_id"]},
        {"$set": {"quantity": total_quantity, "amount": total_amount}},
    )
    if updated_checkout.acknowledged:
        return {"detail": "Successfully Added"}


@router.put("/", status_code=status.HTTP_200_OK)
def remove_checkout(data: UpdateCheckout):
    data_dict = data.model_dump()
    print(data_dict)
