from fastapi import APIRouter, Depends, HTTPException, status, Request
from ..models.auth import get_user, user_dereference
from ..models.checkout import Checkout
from ..db.mongodb import user_collection, product_collection, checkout_collection
from bson import ObjectId, DBRef
from ..models.product import product_dereference
from pymongo import InsertOne

router = APIRouter()


@router.post("/")
def add_new_item(request: Request, data: Checkout, user=Depends(get_user)):
    # session = request.session
    # cart = session.get('cart')
    # operations = []
    # for product_id, quantity in cart.items():
    #     product = DBRef('products', ObjectId(product_id), 'ecommerce')
    #     operations.append(InsertOne({}))
    # return
    data_dict = data.model_dump()
    user_dbref = DBRef("users", ObjectId(user["_id"]), "ecommerce")
    product = product_collection.find_one({"_id": ObjectId(data_dict["product"])})
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not product["item"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient product"
        )
    product_dbref = DBRef("products", ObjectId(product["_id"]), "ecommerce")
    checkout = checkout_collection.find_one({"user": user_dbref})
    if not checkout:
        new_checkout = checkout_collection.insert_one(
            {"user": user_dbref, "products": [product_dbref], "total": product["price"]}
        )
        if new_checkout.inserted_id:
            return HTTPException(status_code=status.HTTP_201_CREATED)
    products = checkout["products"]
    products.append(product_dbref)
    total = checkout["total"]
    total += product["price"]
    updated_checkout = checkout_collection.update_one(
        {"_id": checkout["_id"]}, {"$set": {"products": products, "total": total}}
    )
    if updated_checkout.matched_count:
        product_collection.update_one({"_id": product["_id"]}, {"$inc": {"item": -1}})
        return HTTPException(
            status_code=status.HTTP_200_OK, detail="Checkout update success"
        )


@router.put("/increase")
def increase_item(data: Checkout, user=Depends(get_user)):
    data_dict = data.model_dump()
    user_dbref = DBRef("users", ObjectId(user["_id"]), "ecommerce")
    product = product_collection.find_one({"_id": ObjectId(data_dict["product"])})
    if not product["item"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient product"
        )
    product_dbref = DBRef("products", ObjectId(data_dict["product"]), "ecommerce")
    checkout = checkout_collection.find_one({"user": user_dbref})
    products = checkout["products"]
    products.append(product_dbref)
    total = checkout["total"]
    total += product["price"]

    updated_checkout = checkout_collection.update_one(
        {"_id": checkout["_id"]}, {"$set": {"products": products, "total": total}}
    )
    if updated_checkout.matched_count:
        product_collection.update_one(
            {"_id": ObjectId(data_dict["product"])}, {"$inc": {"item": -1}}
        )
        return HTTPException(
            status_code=status.HTTP_200_OK, detail="Checkout update success"
        )


@router.put("/decrease")
def decrease_item(data: Checkout, user=Depends(get_user)):
    data_dict = data.model_dump()
    user_dbref = DBRef("users", ObjectId(user["_id"]), "ecommerce")
    product = product_collection.find_one({"_id": ObjectId(data_dict["product"])})
    product_dbref = DBRef("products", ObjectId(data_dict["product"]), "ecommerce")
    checkout = checkout_collection.find_one({"user": user_dbref})
    products = checkout["products"]
    products.remove(product_dbref)
    total = checkout["total"]
    total -= product["price"]

    if not total:
        checkout_collection.delete_one({"_id": checkout["_id"]})
    else:
        checkout_collection.update_one(
            {"_id": checkout["_id"]}, {"$set": {"products": products, "total": total}}
        )
    product_collection.update_one(
        {"_id": ObjectId(data_dict["product"])}, {"$inc": {"item": 1}}
    )
    return HTTPException(
        status_code=status.HTTP_200_OK, detail="Checkout update success"
    )


@router.get("/")
def get_checkout(user=Depends(get_user)):
    user_dbref = DBRef("users", ObjectId(user["_id"]), "ecommerce")
    checkout = checkout_collection.find_one({"user": user_dbref})
    checkout["_id"] = str(checkout["_id"])
    checkout["user"] = user_dereference(checkout["user"])
    products = []
    for product in checkout["products"]:
        product = product_dereference(product)
        products.append(product)
    checkout["products"] = products
    return checkout
