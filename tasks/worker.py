import multiprocessing
import os
import tempfile
import boto3
from celery import Celery
import ffmpeg
from ffmpeg_streaming import S3
from loguru import logger
from configs.Environment import get_environment_variables
from ml.model import model

env = get_environment_variables()

celery = Celery("tasks", broker=env.REDIS_HOST)

celery.conf.update(
    worker_log_level='INFO',
)

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

        temp_avi = os.path.join(temp_dir, f"predict/{os.path.splitext(name)[0]}.avi")

        logger.debug("created the tmp dir")

        mkdir(temp_hls)

        logger.debug("writing the mp4")
        with open(temp_mp4, 'wb') as f:
            f.write(stream)

        logger.debug("predicting")
        model.predict(source=temp_mp4, project=temp_dir, save=True, conf=0.65)

        logger.debug("converting")
        logger.debug(temp_avi)

        ffmpeg.input(temp_avi).output(
            f"{temp_hls}/{name}.m3u8",
            format="hls",
            start_number=0,
            hls_time=5,
            hls_list_size=0
        ).run()

        logger.debug("uploading")
        minio.upload_directory(temp_hls, folder=name, bucket_name="static")
