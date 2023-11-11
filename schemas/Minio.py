import datetime
import uuid

from pydantic import BaseModel


class MinioSchema(BaseModel):
    id: uuid.UUID
    name: str
    path: str
    created: datetime.datetime






