import uuid
from sqlalchemy.orm import mapped_column, Mapped

from models.BaseModel import EntityMeta


class MinioStorage(EntityMeta):
    __tablename__ = "minio_storage"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=False)
    path: Mapped[str] = mapped_column(unique=True)

    def normalize(self):
        return {
            "id": self.id.__str__(),
            "name": self.name.__str__(),
            "path": self.path.__str__(),
        }
