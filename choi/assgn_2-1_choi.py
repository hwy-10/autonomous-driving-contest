import cv2
from ultralytics import YOLO

# HSV 색상 기반 신호 판단 함수
def get_traffic_color(cropped_img):
    hsv = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2HSV)

    red_lower1 = (0, 100, 100)
    red_upper1 = (10, 255, 255)
    red_lower2 = (160, 100, 100)
    red_upper2 = (180, 255, 255)
    green_lower = (40, 100, 100)
    green_upper = (90, 255, 255)

    red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
    red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
    green_mask = cv2.inRange(hsv, green_lower, green_upper)

    red_pixels = cv2.countNonZero(red_mask1) + cv2.countNonZero(red_mask2)
    green_pixels = cv2.countNonZero(green_mask)

    if red_pixels > green_pixels and red_pixels > 50:
        return "red"
    elif green_pixels > red_pixels and green_pixels > 50:
        return "green"
    else:
        return "unknown"

# 1. 모델 로드
print("🚦 YOLOv8 모델 로드 중...")
model = YOLO('yolov8n.pt')  # 또는 커스텀 모델 경로
print("✅ 모델 로드 완료")

# 2. 비디오 로드
video_path = "../media_file/traffic_light.mp4"  # 경로 주의!
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("❌ 비디오 로드 실패:", video_path)
    exit()

# 비디오 저장 설정 (선택)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter("result_traffic.avi", fourcc, 30.0, (640, 480))

cv2.namedWindow("Traffic Light Detection", cv2.WINDOW_NORMAL)

# 3. 영상 처리 루프
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))
    results = model(frame, verbose=False)[0]
    status_text = ""

    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        class_name = model.names[cls_id]

        if class_name != "traffic light" or conf < 0.4:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cropped = frame[y1:y2, x1:x2]
        light_color = get_traffic_color(cropped)

        label = f"{class_name} {conf:.2f}"
        color = (0, 255, 0) if light_color == "green" else (0, 0, 255)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        if light_color == "red":
            status_text = "Stop"
        elif light_color == "green":
            status_text = "Go"

    if status_text:
        cv2.putText(frame, status_text, (220, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 4)

    # 출력
    out.write(frame)
    cv2.imshow("Traffic Light Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 정리
cap.release()
out.release()
cv2.destroyAllWindows()
