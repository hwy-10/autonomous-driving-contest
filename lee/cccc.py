import cv2
from ultralytics import YOLO

# 1. YOLOv8 모델 로드 (v8n: nano / v8s / v8m / v8l / v8x 가능)
model = YOLO('yolov8n.pt')  # 가볍고 빠름

# 2. 비디오 열기
video_path = 'C:/Users/user/Desktop/AFB/L_6/roadcam.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("❌ 비디오를 열 수 없습니다.")
    exit()

# 3. 클래스 필터 (자동차/트럭/버스 등)
vehicle_classes = ['car', 'truck', 'bus', 'motorbike']

# 4. 실시간 프레임 분석
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO 추론
    results = model(frame)[0]  # 첫 번째 결과만

    for box in results.boxes:
        cls_id = int(box.cls[0])
        class_name = model.names[cls_id]
        conf = float(box.conf[0])

        # 차량 클래스만 필터링
        if class_name not in vehicle_classes:
            continue

        # 좌표 추출
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        label = f'{class_name} {conf:.2f}'

        # 바운딩 박스 및 라벨 그리기
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 프레임 출력
    cv2.imshow('Vehicle Detection', frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC로 종료
        break

cap.release()
cv2.destroyAllWindows()
