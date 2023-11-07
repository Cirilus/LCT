import io
import os
from typing import List
import cv2
from fastapi import APIRouter, WebSocket, UploadFile, File, HTTPException, status
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
    "/rl"
)
async def get_stream_video(websocket: WebSocket):
    # rtsp_url = "rtsp://admin:A1234567@188.170.176.190:8027/Streaming/Channels/101"
    await websocket.accept()

    rtsp_url = await websocket.receive_text()

    # rtsp_url = "rtsp://admin:A1234567@188.170.176.190:8027/Streaming/Channels/101?transportmode=unicast&profile=Profile_1"

    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cannot open the rcp url")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        ret, buffer = cv2.imencode('.jpg', frame)
        jpg_as_bytes = io.BytesIO(buffer.tobytes())
        await websocket.send_bytes(jpg_as_bytes.getvalue())
        await websocket.receive_text()
