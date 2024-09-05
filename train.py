import os
from ultralytics import YOLO

current_dir = os.getcwd()
model = YOLO("yolov8n-cls.pt" )
model = model(data= current_dir + "/Dice-1", epochs=30)