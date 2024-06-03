from fastapi import APIRouter, Depends, status
from ..models.image import Image
from ..db.mongodb import image_collection
from ..models.auth import get_user

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def image_create(images: Image, user=Depends(get_user)):
    image_dict = images.model_dump()
    img_ids = []
    for i in image_dict.get("img_links"):
        image = image_collection.insert_one({"img_url": i})
        img_ids.append(str(image.inserted_id))
    return img_ids
