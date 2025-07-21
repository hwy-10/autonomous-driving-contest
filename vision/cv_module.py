import os
import cv2
import numpy as np
from config import Status

def get_cv_status(frame):
    # 1. Resize & HSV 마스크
    frame = cv2.resize(frame, (640, 480))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 50, 255]))
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # 2. Grayscale + ROI
    gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    h = gray.shape[0]
    gray[h // 2:, :] = 0  # 상단 제거

    # 3. Morphology
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closing = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
    opening = cv2.erode(opening, kernel, iterations=1)

    # 4. Canny + Contour
    _, binary = cv2.threshold(opening, 160, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(binary)
    cv2.drawContours(filled, contours, -1, 255, thickness=cv2.FILLED)
    edges = cv2.Canny(filled, 20, 150)

    # 5. 중심 계산
    y_target = 390
    white_indices = np.where(edges[y_target] == 255)[0]
    fixed_white_x = 320

    if len(white_indices) >= 2:
        x_left = white_indices[0]
        x_right = white_indices[-1]
        mid_x = (x_left + x_right) // 2

        if mid_x < fixed_white_x - 20:
            return Status.left
        elif mid_x > fixed_white_x + 20:
            return Status.right
        else:
            return Status.go
    else:
        # 차선 탐지 실패 → go로 처리 (또는 stop 등 선택 가능)
        return Status.go
    
    