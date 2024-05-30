from pydantic import BaseModel


class Image(BaseModel):
    img_links: list[str]
