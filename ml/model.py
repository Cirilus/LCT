import cv2
from ultralytics import YOLO

model = YOLO("best.pt")


print(model.predict(source="test1.mp4"))


def detect(video_path):
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter("test/test.mp4", fourcc, fps, (width, height))

