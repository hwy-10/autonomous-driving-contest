import cv2
from ultralytics import YOLO
from collections import deque

# 중심 좌표 버퍼 (최근 좌표 추적)
center_points = deque(maxlen=10)
frame_counter = 0
direction_text = ""
last_yolo_center = None  # 최근 YOLO가 인식한 개의 중심 좌표

# YOLOv8 모델 로드
print("YOLOv8 모델 로드 중...")
model = YOLO('yolov8n.pt')
print("모델 로드 완료")

# 배경 차분기 생성 (YOLO 감지 실패 시 대체용)
bg_subtractor = cv2.createBackgroundSubtractorMOG2()

# 비디오 로드
video_path = "../media_file/dog.mp4"

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("❌ 비디오 로드 실패:", video_path)
    exit()

# 결과 영상 저장 설정
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter("result_dog.avi", fourcc, 30.0, (640, 480))

cv2.namedWindow("dog obstacle avoidance", cv2.WINDOW_NORMAL)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))
    fg_mask = bg_subtractor.apply(frame)  # 배경 차분 결과 저장
    results = model(frame, verbose=False)[0]
    frame_counter += 1

    found_dog = False
    cx = None

    # YOLO로 개 탐지 시도
    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        class_name = model.names[cls_id]

        if class_name != "dog" or conf < 0.25:
            continue

        # 개를 감지한 경우
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        found_dog = True
        last_yolo_center = (cx, cy)  # 가장 최근 YOLO 위치 업데이트

        # 시각화
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{class_name} {conf:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        break  # 첫 번째 개만 추적

    # YOLO 실패 시 → 배경 차분으로 대체 추적
    if not found_dog and last_yolo_center is not None:
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > 500:  # 너무 작으면 무시
                x, y, w, h = cv2.boundingRect(largest)
                fallback_cx = x + w // 2
                fallback_cy = y + h // 2

                # 최근 YOLO 중심과 거리 비교
                dist = abs(fallback_cx - last_yolo_center[0])
                if dist < 50:  # 50px 이내면 같은 개로 간주
                    cx = fallback_cx
                    found_dog = True  # 감지 성공으로 간주
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.putText(frame, "Fallback Tracking", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # 중심좌표 버퍼 업데이트
    if found_dog and cx is not None:
        center_points.append(cx)
    elif center_points:
        center_points.append(center_points[-1])  # 마지막 위치 유지

    # ↔ 이동 방향 판단
    if len(center_points) >= 2:
        diff = center_points[-1] - center_points[0]
        if abs(diff) > 20:
            if diff > 0:
                direction_text = "Avoid to the right"
            else:
                direction_text = "Avoid to the left"
            frame_counter = 0

    # 텍스트 2초간 유지
    if frame_counter < 60 and direction_text:
        cv2.putText(frame, direction_text, (100, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)

    out.write(frame)
    cv2.imshow("dog obstacle avoidance", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 종료 처리
cap.release()
out.release()
cv2.destroyAllWindows()
