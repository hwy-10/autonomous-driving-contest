from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(

    data="C:/Users/user/Desktop/activity/미제연 자율주행/car.v5i.yolov8/data.yaml",
    epochs=50,
    imgsz=640,
    batch=16
)
