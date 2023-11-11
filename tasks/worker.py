import os
import tempfile

import boto3
from celery import Celery
import ffmpeg
from ffmpeg_streaming import S3

from configs.Environment import get_environment_variables
from configs.Database import get_db_connection

env = get_environment_variables()

celery = Celery("tasks", broker=env.REDIS_HOST)

minio = S3(
    aws_access_key_id=env.MINIO_ACCESS,
    aws_secret_access_key=env.MINIO_SECRET,
    endpoint_url=f"http://{env.MINIO_HOST}",
    use_ssl=False,
    verify=False,
    config=boto3.session.Config(signature_version='s3v4'),
)


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


@celery.task
def mp4_to_hls_minio(stream: bytes, name: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_mp4 = os.path.join(temp_dir, f"{name}")

        temp_hls = os.path.join(temp_dir, f"{name}_hls")

        mkdir(temp_hls)

        with open(temp_mp4, 'wb') as f:
            f.write(stream)

        print(temp_hls)

        ffmpeg.input(temp_mp4).output(
            f"{temp_hls}/{name}.m3u8",
            format="hls",
            start_number=0,
            hls_time=5,
            hls_list_size=0
        ).run()

        minio.upload_directory(temp_hls, folder=name, bucket_name="static")
