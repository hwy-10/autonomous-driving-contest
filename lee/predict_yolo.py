from ultralytics import YOLO

model = YOLO("runs/detect/train6/weights/best.pt")

model.predict(
    source="C:/Users/user/Desktop/activity/미제연 자율주행/test_images",
    conf=0.1,
    save=True,
    show=True,             # ← 결과 이미지 즉시 확인 가능 (창 뜸)
    save_txt=True,         # ← 탐지 결과 라벨을 .txt로 저장
    name="predict_pic"    # ← 폴더 이름을 명시적으로 설정
)
