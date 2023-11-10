import os
import tempfile

import ffmpeg_streaming
from ffmpeg_streaming import S3, CloudManager, Formats
from minio import Minio
from configs.Environment import get_environment_variables


env = get_environment_variables()

bucket = "static"

minio_client = Minio(
    env.MINIO_HOST,
    access_key=env.MINIO_ACCESS,
    secret_key=env.MINIO_SECRET,
    secure=False
)

ffmpeg_minio = S3(
    aws_access_key_id=env.MINIO_ACCESS,
    aws_secret_access_key=env.MINIO_SECRET,
    endpoint_url=f"http://{env.MINIO_HOST}"
)

