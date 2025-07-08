import cv2
import numpy as np

# 이미지 읽기
img = cv2.imread('L_5/line.jpg')

# HSV 변환
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# 흰색 범위 정의 (차선 기준)
lower_white = np.array([0, 0, 200])
upper_white = np.array([180, 30, 255])
mask = cv2.inRange(hsv, lower_white, upper_white)

# ROI(하단부만 마스킹)
height, width = mask.shape
roi_mask = np.zeros_like(mask) # 원하는 ROI 영역을 위한 마스크 생성
roi_vertices = np.array([[
    (0, height),    # 이미지 하단 왼쪽
    (0, int(height * 0.35)),  # 이미지 상단 왼쪽
    (width, int(height * 0.35)), # 이미지 상단 오른쪽
    (width, height)  # 이미지 하단 오른쪽
]], dtype=np.int32)
cv2.fillPoly(roi_mask, roi_vertices, 255) 
## 결과 -> 하단 65% 영역만 마스킹 / 나머지는 검정색 (무시영역)

# ROI 적용
masked = cv2.bitwise_and(mask, roi_mask)

# 컨투어 검출
contours, _ = cv2.findContours(masked, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 컨투어 그리기
result = img.copy()
cv2.drawContours(result, contours, -1, (0, 255, 0), 2)

# 결과 출력
cv2.imshow("ROI + Mask", masked)
cv2.imshow("Detected Lane Only", result)
cv2.waitKey(0)
cv2.destroyAllWindows()