import uuid
from datetime import datetime
from typing import List, Type

from fastapi import Depends
from loguru import logger
from sqlalchemy import or_

from configs.Database import get_db_connection
from models.MinioStorage import MinioStorage
from sqlalchemy.orm import Session, lazyload
from utils.errors import ErrEntityNotFound


class MinioStorageRepository:
    def __init__(self, db: Session = Depends(get_db_connection)):
        self.db = db

    def get_list(self) -> list[Type[MinioStorage]]:
        logger.debug("Minio - Repository - get_list")
        query = self.db.query(MinioStorage)
        minio_list = query.all()
        return minio_list

    def get_by_id(self, id: uuid.UUID) -> Type[MinioStorage]:
        logger.debug("MinioStorage - Repository - get_by_id")
        history = self.db.get(
            MinioStorage,
            id
        )
        if history is None:
            raise ErrEntityNotFound("error entity not found")
        return history

    def create(self, file: Type[MinioStorage]) -> Type[MinioStorage]:
        logger.debug("MinioStorage - Repository - create")
        self.db.add(file)
        self.db.commit()
        self.db.refresh(file)
        return file

    def delete(self, file: Type[MinioStorage]) -> None:
        logger.debug("MinioStorage - Repository - delete")
        self.db.delete(file)
        self.db.commit()
        self.db.flush()
