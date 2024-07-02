from ..db.mongodb import db


def image_dereference(img_dbref):
    if not img_dbref:
        return None
    image = db.dereference(img_dbref)
    if image:
        image["_id"] = str(image["_id"])
    return image
