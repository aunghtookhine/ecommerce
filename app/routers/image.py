from fastapi import APIRouter, HTTPException, status
from ..models.image import Image
from ..db.mongodb import image_collection

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def image_create(images: Image):
    image_dict = images.model_dump()
    img_ids = []
    for i in image_dict.get("img_links"):
        image = image_collection.insert_one({"img_url": i})
        img_ids.append(str(image.inserted_id))
    return img_ids
