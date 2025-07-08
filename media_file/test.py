import cv2
import numpy as np
import time

# 고정 파라미터 설정
THRESHOLD_VAL = 160
CANNY_LOW = 20
CANNY_HIGH = 150
BLUR_KERNEL_INDEX = 5   # 실제 kernel size = 2*index + 1 = 11
BLUR_SIGMA = 2

# HSV 범위 설정 (예: 흰색 검출 범위)
HSV_LOWER = np.array([0, 0, 200])
HSV_UPPER = np.array([180, 50, 255])

# 구조화 커널 정의
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))

# 이미지 순차 처리
for i in range(1, 55):  # frame(1) ~ frame(54)
    image_path = f"pict/frame({i}).jpg"
    frame = cv2.imread(image_path)

    if frame is None:
        print(f"Failed to load image: {image_path}")
        continue

    frame = cv2.resize(frame, (640, 480))  # 사진 크기 조정
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # HSV로 변환

    # HSV 마스크 적용
    hsv_mask = cv2.inRange(hsv, HSV_LOWER, HSV_UPPER)
    hsv_result = cv2.bitwise_and(frame, frame, mask=hsv_mask)

    # 그레이스케일 변환 후 상단 1/2 제거
    gray = cv2.cvtColor(hsv_result, cv2.COLOR_BGR2GRAY)
    h = gray.shape[0]
    gray_masked = np.zeros_like(gray)
    gray_masked[h // 2:, :] = gray[h // 2:, :]

    # 형태학적 필터링
    closing = cv2.morphologyEx(gray_masked, cv2.MORPH_CLOSE, kernel)
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)

    # 블러 + 이진화 + Canny 엣지
    ksize = max(1, 2 * BLUR_KERNEL_INDEX + 1)
    blur = cv2.GaussianBlur(opening, (ksize, ksize), BLUR_SIGMA)
    _, binary = cv2.threshold(blur, THRESHOLD_VAL, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(binary)
    cv2.drawContours(filled, contours, -1, 255, thickness=cv2.FILLED)
    edges = cv2.Canny(filled, CANNY_LOW, CANNY_HIGH)

    # y=380 라인에서 흰 픽셀 x 좌표 추출
    y_target = 380
    white_indices = np.where(edges[y_target] == 255)[0]

    # edges 이미지를 컬러로 변환
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    # 기준점
    fixed_white_x = 320

    if len(white_indices) >= 2:
        x_left = white_indices[0]
        x_right = white_indices[-1]
        mid_x = (x_left + x_right) // 2

        # 중점 표시 (빨간 점)
        cv2.circle(edges_colored, (mid_x, y_target), 5, (0, 0, 255), -1)

        # 방향 판단 및 텍스트 출력
        if fixed_white_x - mid_x > 0:
            direction = "left"
        else:
            direction = "right"
        cv2.putText(edges_colored, direction, (30, 60), cv2.FONT_HERSHEY_SIMPLEX,
                    1.5, (0, 255, 0), 3, cv2.LINE_AA)

    # 항상 x=320 위치에 흰 점 표시
    cv2.circle(edges_colored, (fixed_white_x, y_target), 5, (255, 255, 255), -1)

    # 시각화
    cv2.imshow("Original", frame)
    cv2.imshow("Masked Gray (Lower 2/3 only)", gray_masked)
    cv2.imshow("Canny Edge", edges_colored)

    if cv2.waitKey(1000) & 0xFF == 27:
        break

cv2.destroyAllWindows()
