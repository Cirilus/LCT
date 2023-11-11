import cv2
from ultralytics import YOLO

model = YOLO("ml/best.pt")

# model.predict(source=cv2.VideoCapture(fl), project="test", save=True)
