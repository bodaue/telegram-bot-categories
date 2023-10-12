from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel


class User(BaseModel):
    _id: int
    name: str
    username: str
    date: datetime
    role: ObjectId
    category: ObjectId
