import cv2
from motor_control.front_forward import front_forward
from motor_control.rear_forward import rear_forward
from runtime.gpio import led 
def avoid(gray) : # 왼쪽과 오른쪽 차선 중 점선 부분으로 회피
    h, w = gray.shape[:2]
    # 1. Threshold
    _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

    # 2. ROI: 아래쪽 부분만 추출
    roi = binary[int(h*0.6):h, :]

    # 3. 왼쪽/오른쪽 나눠서 점선 개수 카운트
    left_half = roi[:, :w//2]
    right_half = roi[:, w//2:]

    left_count = cv2.countNonZero(left_half)
    right_count = cv2.countNonZero(right_half)

    if left_count > right_count * 1.3:
        led(True, False)
        front_forward(180, 60)
        rear_forward(180, 60)
    elif right_count > left_count * 1.3:
        led(False, True)
        front_forward(180, 120)
        rear_forward(180, 120)
    else: 
        front_forward(180)
        rear_forward(180)
        print("aviod else case")