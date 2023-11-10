import io
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, Header
from fastapi.responses import StreamingResponse
import cv2
from typing import List

from models.MinioStorage import MinioStorage
from services.Minio import MinioStorageService
from schemas.Minio import MinioSchema
from utils.wrappers import error_wrapper

router = APIRouter(prefix="/api/v1/ml", tags=["company"])


@router.post(
    "/load",
    description="loading the video",
    response_model=MinioSchema
)
async def load_video(video: UploadFile = File(...), minio_service: MinioStorageService = Depends()):
    video_content = await video.read()
    video_stream = io.BytesIO(video_content)

    file = MinioStorage(
        name=video.filename,
        path="",
    )

    result = await minio_service.create(file, video_stream, video_content)

    return result.normalize()


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

        ret, buffer = cv2.imencode(".jpg", frame)

        if not ret:
            continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() + b'\r\n')


@router.get("/rl")
async def video_feed(url_rtsp: str):
    return StreamingResponse(streamer(url_rtsp), media_type="multipart/x-mixed-replace;boundary=frame")
