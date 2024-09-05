from ultralytics import YOLO

model = YOLO("yolov8n-cls.pt" )
model = model(data="/Users/sergeysergienko/Library/Mobile Documents/com~apple~CloudDocs/Projects/newton/Dice-1", epochs=30)