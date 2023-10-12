from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel


class Category(BaseModel):
    _id: ObjectId
    created_by: int
    name: str
    date: datetime
