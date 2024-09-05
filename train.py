from ultralytics import YOLO

model = YOLO("yolov8n-cls.pt" )
model = model(data="/home/sergienko/newton/Dice-1", epochs=30)