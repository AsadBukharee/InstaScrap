import uuid
import datetime
from typing import Optional

from fastapi_users import schemas
from pydantic import BaseModel


class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name: str
    birthdate: Optional[datetime.date]


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    birthdate: Optional[datetime.date]


class UserUpdate(schemas.BaseUserUpdate):
    first_name: Optional[str]
    birthdate: Optional[datetime.date]


class MyModel(BaseModel):
    data: str