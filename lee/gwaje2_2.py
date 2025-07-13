import cv2
from ultralytics import YOLO
from collections import deque
import time

# 모델 로드
model = YOLO("yolov8n.pt")  # 정확도 더 원하면 yolov8m.pt 사용

# 비디오 로드
video_path = "C:/Users/user/Desktop/activity/미제연 자율주행/git-clones/autonomous-driving-contest/media_file/dog.mp4"
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("❌ 비디오 열기 실패:", video_path)
    exit()

# 중심 좌표 버퍼
center_buffer = deque(maxlen=10)

# 회피 텍스트 상태
avoid_text = ""
avoid_start_time = 0
avoid_display_duration = 2  # seconds

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)[0]
    dog_detected = False

    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        class_name = model.names[cls_id]

        if class_name != "dog":
            continue

        dog_detected = True
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        center_buffer.append(cx)

        # bounding box + confidence + label
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 200, 0), 2)
        cv2.putText(frame, f'dog {conf:.2f}', (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)

        # 이동 방향 판단
        if len(center_buffer) >= 5:
            delta = center_buffer[-1] - center_buffer[0]
            if abs(delta) > 15:
                if delta > 0:
                    avoid_text = "Avoid to the right"
                else:
                    avoid_text = "Avoid to the left"
                avoid_start_time = time.time()

    # 텍스트 표시 (2초간 유지)
    if time.time() - avoid_start_time < avoid_display_duration and avoid_text:
        cv2.putText(frame, avoid_text, (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

    # 출력
    cv2.imshow("dog obstacle avoidance", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
