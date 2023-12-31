import io
import uuid

import ffmpeg
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
import cv2
from typing import List

from models.MinioStorage import MinioStorage
from services.Minio import MinioStorageService
from schemas.Minio import MinioSchema
from utils.wrappers import error_wrapper
from ml.model import model

router = APIRouter(prefix="/api/v1/ml", tags=["company"])


@router.post(
    "/load",
    description="loading the video",
    response_model=MinioSchema
)
async def load_video(background_tasks: BackgroundTasks, video: UploadFile = File(...),
               minio_service: MinioStorageService = Depends(), ):
    video_content = video.file.read()
    video.file.seek(0)
    video_stream = io.BytesIO(video_content)

    file = MinioStorage(
        name=video.filename,
        path="",
    )

    result = await minio_service.create(file, video_stream, video_content, background_tasks)

    return result.normalize()


@router.get(
    "/check",
    description="returning the list of the files",
)
async def check_if_exist(id: uuid.UUID, minio_service: MinioStorageService = Depends()):
    file = error_wrapper(minio_service.check_if_exist, id)

    return {"url": f"static/{file.path}/{file.path}.m3u8"}


@router.get(
    "/list",
    description="returning the list of the files",
    response_model=List[MinioSchema],
)
async def list_file(minio_service: MinioStorageService = Depends()):
    results = error_wrapper(minio_service.get_list)

    return [result.normalize() for result in results]


@router.get(
    "/get",
    description="returning the info about file"
)
async def get_file(id: uuid.UUID, minio_service: MinioStorageService = Depends()):
    result = error_wrapper(minio_service.get_by_id, id)

    return result.normalize()


@router.get(
    "/get_link",
    description="returning the info about file"
)
async def get_file(id: uuid.UUID, minio_service: MinioStorageService = Depends()):
    result = error_wrapper(minio_service.get_link, id)

    return {"url": result}


def streamer(url_rtsp: str):
    cap = cv2.VideoCapture(url_rtsp)
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        model.predict(source=frame, stream=True)

        ret, buffer = cv2.imencode(".jpg", frame)

        if not ret:
            continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() + b'\r\n')


@router.get("/rl")
async def video_feed(url_rtsp: str):
    return StreamingResponse(streamer(url_rtsp), media_type="multipart/x-mixed-replace;boundary=frame")


@router.get("/rl_hls")
async def video_feed(url_rtsp: str):
    ffmpeg_cmd = (
        ffmpeg.input(url_rtsp, rtsp_transport="tcp")
        .output("pipe:", format="hls", hls_time=2, hls_list_size=5)
        .run_async(pipe_stdout=True)
    )

    async def generate():
        try:
            while True:

                chunk = ffmpeg_cmd.stdout.read(1024)
                if not chunk:
                    break
                yield chunk
        finally:

            ffmpeg_cmd.stdout.close()
            await ffmpeg_cmd.wait()

    return StreamingResponse(generate(), media_type="application/vnd.apple.mpegurl")
