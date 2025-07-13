from ultralytics import YOLO

model = YOLO('yolov8n.pt')  # 사전학습 모델로 transfer learning
model.train(
    data='C:/Users/허윤/Desktop/대외활동/미래제품연구회/자율주행/자율주행_코드/t_light-1/data.yaml',
    epochs=5,
    imgsz=640,
    batch=16,
)
