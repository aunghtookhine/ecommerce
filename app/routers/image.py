from fastapi import (
    APIRouter,
    Depends,
    status,
    Form,
    UploadFile,
    HTTPException,
    File,
    Request,
)
from fastapi.responses import RedirectResponse
from ..db.mongodb import image_collection
from ..models.auth import get_user
from bson import ObjectId
import os
import hashlib
import datetime
from dotenv import load_dotenv
import os

router = APIRouter()
load_dotenv(override=True)


@router.post("/")
async def upload(
    request: Request,
    name: str = Form(...),
    file: UploadFile = File(...),
    token: str = Form(...),
    is_category: bool = Form(default=True),
):
    user = get_user(request, token)
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
    date = datetime.datetime.now().strftime("%d-%b-%Y-%H_%M_%S")
    _, file_ext = os.path.splitext(file.filename)
    name = name.strip().lower().split()
    name = "-".join(name)
    file_name = f"{name}-{date}{file_ext}"
    os.makedirs(os.getenv("CATEGORY_DIR"), exist_ok=True)
    os.makedirs(os.getenv("PRODUCT_DIR"), exist_ok=True)
    path = os.path.join(os.getenv("CATEGORY_DIR"), file_name)
    if not is_category:
        path = os.path.join(os.getenv("PRODUCT_DIR"), file_name)
    with open(path, "wb") as f:
        f.write(contents)
    path = path.replace("static/", "/static/")
    img = image_collection.insert_one(
        {"name": name.strip().lower(), "checksum": checksum, "img_url": path}
    )
    if img.inserted_id:
        return RedirectResponse("/dashboard/images", status_code=status.HTTP_302_FOUND)


@router.get("/")
def find_images(user=Depends(get_user)):
    cursor = image_collection.find({})
    images = []
    for image in cursor:
        image["_id"] = str(image["_id"])
        images.append(image)
    return images


@router.get("/{id}")
def find_image(id: str, user=Depends(get_user)):
    image = image_collection.find_one({"_id": ObjectId(id.strip())})
    if not image:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid image id"
        )
    image["_id"] = str(image["_id"])
    return image


@router.post("/{id}", status_code=status.HTTP_200_OK)
def remove_image(request: Request, id: str, token: str = Form(...)):
    user = get_user(request, token)
    image = image_collection.find_one_and_delete({"_id": ObjectId(id.strip())})
    if not image:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid image id"
        )
    path = image["img_url"]
    path = path.replace("/static", "static")
    os.remove(path)
    return RedirectResponse("/dashboard/images", status_code=status.HTTP_302_FOUND)
