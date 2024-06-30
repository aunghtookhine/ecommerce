images = [
    {'name': 'max-90', 
     'checksum': 'a431522717b05576cc5d8ac77a519759', 
     'img_url': '/static/product/max-90-10-Jun-2024-08_46_21.png'},
    {'name': 'primary', 
     'checksum': '1c3cd06a2d44391705afeacbdcd9ffb3', 
     'img_url': '/static/product/primary-10-Jun-2024-08_45_05.jpeg'},
    {'name': 'solo-swoosh', 
     'checksum': '807335967a21af0fe7e56199c6b83540', 
     'img_url': '/static/product/solo-swoosh-10-Jun-2024-08_45_19.jpeg'},
    {'name': 'solo-swoosh', 
     'checksum': '30d99fd4511baab38dab8e7af7232d9d', 
     'img_url': '/static/product/solo-swoosh-10-Jun-2024-08_45_42.png'},
    {'name': 'solo-swoosh', 
     'checksum': 'ef9117cd0c0c90708c879970d1ab590d', 
     'img_url': '/static/product/solo-swoosh-10-Jun-2024-08_45_53.png'}
]

from pymongo import MongoClient
from fastapi import HTTPException, status

from dotenv import load_dotenv
import os

load_dotenv(override=True)

try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DATABASE_NAME")]
    user_collection = db["users"]
    category_collection = db["categories"]
    product_collection = db["products"]
    image_collection = db["images"]
    checkout_collection = db["checkouts"]
except:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Database Connection Error",
    )

for image in images:
    image_collection.insert_one({'name': image['name'], 'checksum': image['checksum'], 'img_url': image['img_url']})
