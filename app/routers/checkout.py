from fastapi import APIRouter, status, HTTPException, Depends
from ..models.checkout import Checkout, UpdateCheckout
from ..db.mongodb import product_collection, checkout_collection
from bson import ObjectId
from ..models.auth import get_user

router = APIRouter()


@router.post("/", status_code=status.HTTP_200_OK)
def checkout(data: Checkout, user=Depends(get_user)):
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


@router.put("/decrease", status_code=status.HTTP_200_OK)
def decrease_quantity(data: UpdateCheckout, user=Depends(get_user)):
    data_dict = data.model_dump()
    product = product_collection.find_one({"_id": ObjectId(data_dict["product_id"])})
    checkout_collection.update_one(
        {"user_id": data_dict["user_id"], "product_id": data_dict["product_id"]},
        {"$inc": {"quantity": -1, "amount": -product["price"]}},
    )
    updated_checkout = checkout_collection.find_one(
        {"user_id": data_dict["user_id"], "product_id": data_dict["product_id"]}
    )
    product_collection.update_one(
        {"_id": ObjectId(data_dict["product_id"])}, {"$inc": {"item": 1}}
    )
    if not updated_checkout["quantity"]:
        checkout_collection.delete_one(
            {"user_id": data_dict["user_id"], "product_id": data_dict["product_id"]},
        )
    return {"detail": "Successfully updated"}


@router.put("/increase", status_code=status.HTTP_200_OK)
def increase_quantity(data: UpdateCheckout, user=Depends(get_user)):
    data_dict = data.model_dump()
    product = product_collection.find_one({"_id": ObjectId(data_dict["product_id"])})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Product Id"
        )
    if not product["item"]:
        return {"detail": "Insufficient quantity"}
    product_collection.update_one(
        {"_id": ObjectId(data_dict["product_id"])}, {"$inc": {"item": -1}}
    )
    checkout = checkout_collection.update_one(
        {"product_id": data_dict["product_id"], "user_id": data_dict["user_id"]},
        {"$inc": {"quantity": 1}},
    )
    if checkout.acknowledged:
        return {"detail": "Successfully increased."}
