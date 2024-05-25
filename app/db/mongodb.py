from pymongo import MongoClient
from fastapi import HTTPException, status
from dotenv import load_dotenv
import os

load_dotenv()

try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DATABASE_NAME")]
    user_collection = db["users"]
    category_collection = db["categories"]
except:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
