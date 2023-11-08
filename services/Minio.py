import io
from typing import List, Type

import uuid
from fastapi import Depends, HTTPException
from loguru import logger
from repositories.Minio import MinioStorageRepository
from models.MinioStorage import MinioStorage

from configs.MinioConfig import minio_client, bucket
from minio.error import S3Error

from utils.errors import ErrEntityNotFound


class MinioStorageService:
    def __init__(self,
                 minio_repo: MinioStorageRepository = Depends()):
        self.minio_repo = minio_repo

    def get_list(self) -> list[Type[MinioStorage]]:
        logger.debug("MinioStorage - Service - get_users")
        result = self.minio_repo.get_list()
        return result

    def get_by_id(self, id: uuid.UUID) -> Type[MinioStorage]:
        logger.debug("MinioStorage - Service - get_user_by_id")
        result = self.minio_repo.get_by_id(id)
        return result

    def get_file(self, id: uuid.UUID) -> bytes:
        logger.debug("MinioStorage - Service - get_file")
        result = self.get_by_id(id)

        file = minio_client.get_object(bucket, result.path + result.name)
        return file.read()

    def check_if_exist(self, id: uuid.UUID):
        logger.debug("MinioStorage - Service - check_if_exist")
        result = self.minio_repo.get_by_id(id)

        try:
            minio_client.stat_object(
                bucket,
                result.path + result.name
            )
        except S3Error as e:
            if e.code == 'NoSuchKey':
                raise ErrEntityNotFound("There is no this file in minio")

    def delete(self, id: uuid.UUID) -> None:
        logger.debug("MinioStorage - Service - delete_user")

        result = self.minio_repo.get_by_id(id)

        minio_client.remove_object(
            bucket,
            result.path + result.name
        )

        self.minio_repo.delete(result)
        return None

    def create(self, file: Type[MinioStorage], file_stream: io.BytesIO, file_content: bytes) -> Type[MinioStorage]:
        logger.debug("MinioStorage - Service - create")

        minio_client.put_object(
            bucket,
            file.path + file.name,
            file_stream,
            len(file_content)
        )

        file.id = uuid.uuid4()
        result = self.minio_repo.create(file)
        return result
