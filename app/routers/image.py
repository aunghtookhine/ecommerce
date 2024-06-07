from fastapi import APIRouter, Depends, status, Form, UploadFile, HTTPException, File
from ..db.mongodb import image_collection
from ..models.auth import get_user
from bson import ObjectId
import os
import hashlib
import datetime

router = APIRouter()

IMAGE_DIR = "static/assets"


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
    checksum = hashlib.md5(contents).hexdigest()

    image = image_collection.find_one({"checksum": checksum})
    if image:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Duplicate image"
        )

    date = datetime.datetime.now().strftime("%d-%b-%Y-%H:%M:%S")
    _, file_ext = os.path.splitext(file.filename)
    file_name = f"{name.strip().lower()}-{date}{file_ext}"

    os.makedirs(IMAGE_DIR, exist_ok=True)
    path = os.path.join(IMAGE_DIR, file_name)

    with open(path, "wb") as f:
        f.write(contents)

    path = path.replace("static/", "")
    img = image_collection.insert_one(
        {"name": name.strip().lower(), "checksum": checksum, "img_url": path}
    )
    return {"_id": str(img.inserted_id)}


@router.get("/")
def find_images():
    cursor = image_collection.find({})
    images = []
    for image in cursor:
        image["_id"] = str(image["_id"])
        images.append(image)
    return images


@router.get("/{id}")
def find_image(id: str):
    image = image_collection.find_one({"_id": ObjectId(id.strip())})
    if not image:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid image id"
        )
    image["_id"] = str(image["_id"])
    return image


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_image(id: str):
    image = image_collection.find_one_and_delete({"_id": ObjectId(id.strip())})
    if not image:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid image id"
        )
    img_path = os.path.join("static", image["img_url"])
    os.remove(img_path)
