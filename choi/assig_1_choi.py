import cv2
import numpy as np
import os
import glob

# 고정 파라미터 설정
HSV_LOWER = np.array([0, 0, 200])
HSV_UPPER = np.array([180, 30, 255])

# 이미지 프레임 경로 로딩
frame_dir = "E:/Desktop/MJY-autodrive/track_frames"
frame_paths = sorted(glob.glob(os.path.join(frame_dir, "*.jpg")))

# 이미지 처리 루프 시작
for path in frame_paths:
    frame = cv2.imread(path)
    if frame is None:
        print(f"❌ 이미지 불러오기 실패: {path}")
        continue

    # 프레임 크기 표준화
    frame = cv2.resize(frame, (640, 480))

    # HSV 변환 후 흰색 차선 마스크 생성
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, HSV_LOWER, HSV_UPPER)

    # ROI 다각형 마스크 생성 (하단부 1/2 영역)
    height, width = mask.shape
    roi_mask = np.zeros_like(mask)  # 검정색으로 채워진 빈 마스크
    roi_vertices = np.array([[
        (0, height),                # 좌상단
        (0, int(height * 0.5)),     # 좌하단
        (width, int(height * 0.5)), # 우하단
        (width, height)             # 우상단
    ]], dtype=np.int32)
    cv2.fillPoly(roi_mask, roi_vertices, 255)   # ROI 영역을 흰색으로 채움

    # ROI 마스크 적용
    masked = cv2.bitwise_and(mask, roi_mask)

    # 형태학적 필터링: 노이즈 제거 및 선 연결
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    cleaned = cv2.morphologyEx(masked, cv2.MORPH_OPEN, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)

    # 컨투어 검출
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 컨투어 시각화
    result = frame.copy()
    cv2.drawContours(result, contours, -1, (0, 255, 0), 2)

    # 결과 출력
    cv2.imshow("ROI + Mask", cleaned)
    cv2.imshow("Detected Lane Only", result)

    # 종료 키: ESC 또는 q
    if cv2.waitKey(300) & 0xFF in [27, ord('q')]:
        break

cv2.destroyAllWindows()
