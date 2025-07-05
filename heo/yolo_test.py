import cv2
from ultralytics import YOLO

try:
    print("🚀 YOLO 모델 로드 중...")
    model = YOLO('autonomous-driving-contest/yolov8n.pt')
    print("✅ YOLO 모델 로드 완료")
except Exception as e:
    print("❌ YOLO 모델 로드 실패:", e)
    exit()

try:
    print("🎥 비디오 파일 열기 시도...")
    cap = cv2.VideoCapture("C:/Users/허윤/Desktop/대외활동/미래제품연구회/자율주행/자율주행_코드/autonomous-driving-contest/media_file/roadcam.mp4")
    if not cap.isOpened():
        raise IOError("비디오 파일을 열 수 없습니다.")
    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = int(1000 / fps) if fps > 0 else 30
    print("✅ 비디오 로드 완료, FPS:", fps)
except Exception as e:
    print("❌ 비디오 로드 실패:", e)
    exit()

cv2.namedWindow('YOLO Detection', cv2.WINDOW_NORMAL)

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("⚠️ 더 이상 프레임을 읽을 수 없습니다.")
            break

        frame = cv2.resize(frame, (640, 480))

        # YOLO 예측
        try:
            results = model(frame)[0]
        except Exception as e:
            print("❌ YOLO 예측 실패:", e)
            break

        # 박스 그리기
        try:
            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                label = model.names[cls_id]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        except Exception as e:
            print("❌ 바운딩 박스 그리기 실패:", e)

        cv2.imshow('YOLO Detection', frame)

        if cv2.waitKey(delay) & 0xFF == ord('q'):
            print("🛑 사용자가 종료함.")
            break

except Exception as e:
    print("❌ 루프 중 에러 발생:", e)

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("✅ 프로그램 종료 및 자원 해제 완료.")
