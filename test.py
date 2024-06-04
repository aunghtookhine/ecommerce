from bson import ObjectId

id = "665ea6a1027b1ffbf8793d71"


ID = {"_id": "665ea6a1027b1ffbf8793d71"}

objId = ObjectId(ID.get("_id"))

# print(id)
# print(ID)

print(type(objId))
