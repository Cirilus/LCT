import io
import os
import tempfile
from datetime import timedelta
from typing import Type, List
import uuid

import ffmpeg_streaming
from fastapi import Depends
from ffmpeg_streaming import CloudManager, Formats, Representation, Size, Bitrate
from loguru import logger
from repositories.Minio import MinioStorageRepository
from models.MinioStorage import MinioStorage

import asyncio

from configs.MinioConfig import minio_client, bucket, ffmpeg_minio
from minio.error import S3Error

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

    async def create(self, file: Type[MinioStorage], file_stream: io.BytesIO, file_content: bytes) -> Type[
        MinioStorage]:
        logger.debug("MinioStorage - Service - create")

        file.id = uuid.uuid4()
        file.path = f"{str(file.id)}_{file.name}"

        self.mp4_to_hls_minio(file_stream.getvalue(), file.path)

        result = self.minio_repo.create(file)
        return result

    def mp4_to_hls_minio(self, stream: bytes, name: str):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_mp4 = os.path.join(temp_dir, f"{name}")

            with open(temp_mp4, 'wb') as f:
                f.write(stream)

            to_minio = CloudManager().add(ffmpeg_minio, bucket_name="static", folder=f"{name}/")

            video = ffmpeg_streaming.input(temp_mp4)

            hls = video.hls(Formats.h264())

            _1080p = Representation(Size(1920, 1080), Bitrate(4096 * 1024, 320 * 1024))

            hls.representations(_1080p)

            hls.output(clouds=to_minio, async_run=False)
