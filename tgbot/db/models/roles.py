from bson import ObjectId
from pydantic import BaseModel


class Role(BaseModel):
    _id: ObjectId
    name: str
    password: str
