from pymongo import MongoClient
from fastapi import HTTPException, status
from fastapi import FastAPI
import os

app = FastAPI()


def get_mongo_client(db_url: str, db_name: str) -> MongoClient:
    try:
        client = MongoClient(db_url)
        return client[db_name]
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
