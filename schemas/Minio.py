import uuid

from pydantic import BaseModel


class MinioSchema(BaseModel):
    id: uuid.UUID
    name: str
    path: str






