import os
import cv2
import numpy as np
import time

# 고정 파라미터 설정
THRESHOLD_VAL = 160
CANNY_LOW = 20
CANNY_HIGH = 150
HSV_LOWER = np.array([0, 0, 200])
HSV_UPPER = np.array([180, 50, 255])
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

i = 1
os.makedirs("after_pict", exist_ok=True)
while 1 <= i <= 54:
    
    # 이미지 로드 : 5ms
    total_start = time.time()
    start = time.time()
    image_path = f"pict/frame({i}).jpg"
    frame = cv2.imread(image_path)
    print(f"[이미지 로드] {(time.time() - start)*1000:.2f} ms")

    if frame is None:
        print(f"Failed to load image: {image_path}")
        i += 1
        continue

    # HSV 마스크 적용 : 4ms
    start = time.time()
    frame = cv2.resize(frame, (640, 480))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv_mask = cv2.inRange(hsv, HSV_LOWER, HSV_UPPER)
    hsv_result = cv2.bitwise_and(frame, frame, mask=hsv_mask)
    print(f"[HSV 마스크] {(time.time() - start)*1000:.2f} ms")
    
    # 그레이스케일 및 마스킹 : 1ms
    start = time.time()
    gray = cv2.cvtColor(hsv_result, cv2.COLOR_BGR2GRAY)
    h = gray.shape[0]
    gray_masked = np.zeros_like(gray)
    gray_masked[h // 2:, :] = gray[h // 2:, :]
    print(f"[그레이스케일 필터링] {(time.time() - start)*1000:.2f} ms")

    # 형태학적 필터링 : 2ms
    start = time.time()
    closing = cv2.morphologyEx(gray_masked, cv2.MORPH_CLOSE, kernel)
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
    cv2.imshow("before", opening)
    opening = cv2.erode(opening, kernel, iterations=1)
    cv2.imshow("after", opening)
    print(f"[형태학적 필터링] {(time.time() - start)*1000:.2f} ms")

    # 이진화 + 칸토어 + Canny 엣지 : 4ms
    start = time.time()
    _, binary = cv2.threshold(opening, THRESHOLD_VAL, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(binary)
    cv2.drawContours(filled, contours, -1, 255, thickness=cv2.FILLED)
    edges = cv2.Canny(filled, CANNY_LOW, CANNY_HIGH)
    print(f"[이진화 + 엣지] {(time.time() - start)*1000:.2f} ms")

    # 중점 계산 : 1ms
    start = time.time()
    y_target = 390
    white_indices = np.where(edges[y_target] == 255)[0]
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    fixed_white_x = 320

    if len(white_indices) >= 2:
        x_left = white_indices[0]
        x_right = white_indices[-1]
        mid_x = (x_left + x_right) // 2


        # 방향 텍스트 출력
        if fixed_white_x - mid_x > 0:
            direction = "left"
        else:
            direction = "right"
        
        cv2.circle(edges_colored, (mid_x, y_target), 5, (0, 0, 255), -1)
        cv2.putText(edges_colored, direction, (30, 60), cv2.FONT_HERSHEY_SIMPLEX,
                    1.5, (0, 255, 0), 3, cv2.LINE_AA)

    # 기준점 표시
    cv2.circle(edges_colored, (fixed_white_x, y_target), 5, (255, 255, 255), -1)
    print(f"[중점 처리 시간] {(time.time() - start)*1000:.2f} ms")


    # 결과 이미지 저장
    output_path = f"after_pict/frame({i})_edge.jpg"
    cv2.imwrite(output_path, edges_colored)
    
    # 전체 처리 시간
    print(f"[전체 처리 시간] {(time.time() - total_start)*1000:.2f} ms\n")

    # 시각화
    cv2.imshow("Original", frame)
    cv2.imshow("Canny Edge", edges_colored)

    # 키 입력 대기
    key = cv2.waitKey(0) & 0xFF
    if key == 27:
        break
    elif key == ord('a') and i > 1:
        i -= 1
    elif key == ord('d') and i < 54:
        i += 1

cv2.destroyAllWindows()

# 이미지 전처리에 걸린 시간 : ~20ms