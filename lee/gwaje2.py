import cv2
from ultralytics import YOLO
from collections import deque, Counter

# 1. YOLO 모델 로드
model = YOLO("yolov8n.pt")

# 2. 비디오 로드
video_path = 'media_file/traffic_light.mp4'
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("❌ 비디오 열기 실패:", video_path)
    exit()

# 판단 안정화를 위한 버퍼
decision_buffer = deque(maxlen=5)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)[0]

    # 3. traffic light 클래스만 confidence 0.25 이상 필터링
    threshold_conf = 0.25
    traffic_lights = [box for box in results.boxes
                      if model.names[int(box.cls[0])] == "traffic light"
                      and float(box.conf[0]) > threshold_conf]

    # 상위 2개 박스만 사용
    traffic_lights = sorted(traffic_lights, key=lambda b: float(b.conf[0]), reverse=True)[:2]

    red_detected = False
    green_detected = False

    for box in traffic_lights:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        margin = 5
        x1 = max(x1 + margin, 0)
        y1 = max(y1 + margin, 0)
        x2 = min(x2 - margin, frame.shape[1])
        y2 = min(y2 - margin, frame.shape[0])

        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            continue

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # 4. Red / Green HSV 마스크
        mask_red = cv2.inRange(hsv, (0, 70, 70), (15, 255, 255)) + \
                   cv2.inRange(hsv, (150, 70, 70), (180, 255, 255))
        mask_green = cv2.inRange(hsv, (35, 40, 40), (95, 255, 255))

        red_pixels = cv2.countNonZero(mask_red)
        green_pixels = cv2.countNonZero(mask_green)
        total_pixels = roi.shape[0] * roi.shape[1]

        if total_pixels == 0:
            continue

        red_ratio = red_pixels / total_pixels
        green_ratio = green_pixels / total_pixels
        conf = float(box.conf[0])

        if red_ratio > 0.02:
            red_detected = True
            label = f"Red {conf:.2f}"
            color = (0, 0, 255)
        elif green_ratio > 0.02:
            green_detected = True
            label = f"Green {conf:.2f}"
            color = (0, 255, 0)
        else:
            label = "Unknown"
            color = (200, 200, 200)

        # 5. 박스 및 텍스트 시각화
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # 6. 프레임 판단 결과 버퍼에 추가
    if red_detected:
        decision_buffer.append("Red")
    elif green_detected:
        decision_buffer.append("Green")
    else:
        decision_buffer.append("Unknown")

    # 7. 버퍼 기반 다수결 판단
    counts = Counter(decision_buffer)
    if counts["Red"] >= 3:
        status_text = "Stop"
        text_color = (0, 0, 255)
    elif counts["Green"] >= 3:
        status_text = "Go"
        text_color = (0, 255, 0)
    else:
        status_text = "Unknown"
        text_color = (255, 255, 255)

    # 8. 상단 텍스트 출력
    cv2.putText(frame, status_text, (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 2.0, text_color, 5)

    # 9. 창 표시
    cv2.imshow("Traffic Light Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
