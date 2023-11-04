import io
import os
from typing import List

from fastapi import APIRouter, WebSocket, UploadFile, File
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/v1/ml", tags=["company"])


@router.post(
    "/binary",
    description="get binary video and returning stream"
)
async def get_binary_video(video: UploadFile = File(...)):
    video_stream = await video.read()

    return StreamingResponse(io.BytesIO(video_stream), media_type="video/mp4")


@router.websocket(
    "/socket"
)
async def get_stream_video(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive()
        if isinstance(data, bytes):
            await websocket.send_bytes(data)
        else:
            break

