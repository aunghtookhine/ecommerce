from fastapi import APIRouter, Depends, status, Form, UploadFile, HTTPException, File
from ..db.mongodb import image_collection
from ..models.auth import get_user
from bson import Binary, ObjectId
from fastapi.responses import StreamingResponse
import os

router = APIRouter()

IMAGE_DIR = "assets"


@router.post("/")
async def upload(name: str = Form(...), file: UploadFile = File(...)):
    available_content_types = ["image/png", "image/jpeg"]
    content_type = file.headers.get("content-type")
    if not content_type in available_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unavailable image format",
        )
    contents = await file.read()
    os.makedirs(IMAGE_DIR, exist_ok=True)
    path = os.path.join(IMAGE_DIR, file.filename)
    isImgUrl = image_collection.find_one({"img_url": path})
    if isImgUrl:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Duplicate image"
        )
    with open(path, "wb") as f:
        f.write(contents)

    img = image_collection.insert_one({"name": name, "img_url": path})
    return {"_id": str(img.inserted_id)}


@router.get("/")
def find_images():
    cursor = image_collection.find({})
    images = []
    for image in cursor:
        image["_id"] = str(image["_id"])
        images.append(image)
    return images


@router.get("/{img_name}")
def find_image(img_name: str):
    url = f"http://127.0.0.1:8000/app/images/{img_name}"
    return url
    image = image_collection.find_one({"_id": ObjectId(id.strip())})
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid image id"
        )
    image["_id"] = str(image["_id"])
    return image
