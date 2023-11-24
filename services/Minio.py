import io
import sys
from datetime import timedelta
from typing import Type, List
import uuid

import boto3
import ffmpeg_streaming
from fastapi import Depends, BackgroundTasks
from ffmpeg_streaming import CloudManager, Formats, Representation, Size, Bitrate, S3
from loguru import logger

from configs.Environment import get_environment_variables
from repositories.Minio import MinioStorageRepository
from models.MinioStorage import MinioStorage

import asyncio

from configs.MinioConfig import minio_client, bucket
from minio.error import S3Error

from tasks.worker import mp4_to_hls_minio
from utils.errors import ErrEntityNotFound


class MinioStorageService:
    def __init__(self,
                 minio_repo: MinioStorageRepository = Depends()):
        self.minio_repo = minio_repo

    def get_list(self) -> List[Type[MinioStorage]]:
        logger.debug("MinioStorage - Service - get_users")
        result = self.minio_repo.get_list()
        return result

    def get_by_id(self, id: uuid.UUID) -> Type[MinioStorage]:
        logger.debug("MinioStorage - Service - get_user_by_id")
        result = self.minio_repo.get_by_id(id)
        return result

    def get_link(self, id: uuid.UUID):
        logger.debug("MinioStorage - Service - get_link")
        result = self.get_by_id(id)

        url = minio_client.get_presigned_url(
            "GET",
            bucket,
            result.path,
            expires=timedelta(days=2)
        )
        return url

    def check_if_exist(self, id: uuid.UUID) -> Type[MinioStorage]:
        logger.debug("MinioStorage - Service - check_if_exist")
        result = self.minio_repo.get_by_id(id)

        try:
            minio_client.stat_object(
                bucket,
                f"{result.path}/{result.path}.m3u8",
            )
            return result
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

    async def create(self, file: Type[MinioStorage], file_stream: io.BytesIO, file_content: bytes, background_tasks: BackgroundTasks) -> Type[
        MinioStorage]:
        logger.debug("MinioStorage - Service - create")

        file.id = uuid.uuid4()
        file.path = f"{str(file.id)}_{file.name}"

        # background_tasks.add_task(mp4_to_hls_minio,file_content, file.path)
        mp4_to_hls_minio.delay(file_content, file.path)

        result = self.minio_repo.create(file)
        return result

