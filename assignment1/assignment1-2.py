import cv2
from ultralytics import YOLO

# 1. 모델 로드
try:
    print("🚀 YOLOv8 모델 로드 중...")
    model_v8 = YOLO('autonomous-driving-contest/yolov8n.pt')
    print("✅ 모델 로드 완료")
except Exception as e:
    print("❌ 모델 로드 실패:", e)
    exit()

# 2. 영상 로드
<<<<<<< HEAD
video_path = "C:/Users/user/Desktop/활동/미제연 자율주행/git-clones/autonomous-driving-contest/assignment1/roadcam.mp4"
=======
video_path = "E:/dev_in_E/git-clones-E/autonomous-driving-contest/assignment1/roadcam.mp4"
>>>>>>> 3d675100b5e1db49dd8eb9809cc7f083c5721bd2
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("❌ 비디오 로드 실패:", video_path)
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
delay = int(1000 / fps) if fps > 0 else 30
print("✅ 비디오 로드 완료, FPS:", fps)

# 3. 윈도우 준비
cv2.namedWindow('YOLOv8 Detection', cv2.WINDOW_NORMAL)

# 4. 루프
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("⚠️ 더 이상 프레임을 읽을 수 없습니다.")
        break

    # 프레임 리사이즈
    frame_v8 = cv2.resize(frame, (640, 480))

    # YOLOv8 예측
    try:
        results_v8 = model_v8(frame_v8)[0]
        for box in results_v8.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = model_v8.names[cls_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame_v8, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame_v8, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    except Exception as e:
        print("❌ YOLOv8 예측 오류:", e)

    # 5. 결과 출력
    cv2.imshow('YOLOv8 Detection', frame_v8)

    # 종료 조건
    if cv2.waitKey(delay) & 0xFF == ord('q'):
        print("🛑 사용자 종료 요청")
        break

# 6. 종료
cap.release()
cv2.destroyAllWindows()
print("✅ 프로그램 정상 종료")
