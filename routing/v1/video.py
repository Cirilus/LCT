import io
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
import time
import cv2

router = APIRouter(prefix="/api/v1/ml", tags=["company"])


@router.post(
    "/binary",
    description="get binary video and returning stream"
)
async def get_binary_video(video: UploadFile = File(...)):
    video_stream = await video.read()

    return StreamingResponse(io.BytesIO(video_stream), media_type="video/mp4")


def streamer(url_rtsp: str):
    cap = cv2.VideoCapture(url_rtsp)
    while True:
        time.sleep(0.2)
        ret, frame = cap.read()

        if not ret:
            break

        ret, buffer = cv2.imencode(".jpg", frame)

        if not ret:
            continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(buffer) + b'\r\n')


@router.get("/rl")
async def video_feed(url_rtsp: str):
    return StreamingResponse(streamer(url_rtsp), media_type="multipart/x-mixed-replace;boundary=frame")
