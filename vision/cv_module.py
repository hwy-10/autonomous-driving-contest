import cv2
import numpy as np
from runtime.config import Status

# 조향 각도 관련 상수
ANGLE_CENTER = 90
MAX_ANGLE_OFFSET = 45  # 최대 조향 보정 각도

class PIDController:
    def __init__(self, kp=0.5, ki=0.0, kd=0.1):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def update(self, target, current):
        error = target - current
        self.integral += error
        derivative = error - self.prev_error
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        return current + output

# BEV 변환용 src 포인트 (영상 해상도 640x480 기준)
src_pts = np.array([[170, 290], [440, 290], [564, 390], [80, 390]], dtype=np.float32)

def warp_image(image, src_pts, dst_size=(640, 480)):
    width, height = dst_size
    dst_pts = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(image, M, dst_size)
    return warped

# 핵심 함수
pid = PIDController(kp=0.5, ki=0.0, kd=0.05)
prev_cx = None

def image_preprocessing(frame): # gray까지 이미지 전처리를 함
    bev = warp_image(frame, src_pts)
    gray = cv2.cvtColor(bev, cv2.COLOR_BGR2GRAY)
    return gray

def get_cv_angle(gray):  # gray 이미지를 기반으로 조향 각도 계산
    global prev_cx
    blur = cv2.GaussianBlur(gray, (5, 5), 1.5)
    edges = cv2.Canny(blur, 40, 120)

    # y좌표별 가중 평균 중심 계산
    target_y_list = [(370, 10), (360, 5), (350, 3), (340, 2)]
    weighted_sum, total_weight, cy_roi = 0, 0, None

    for y_val, weight in target_y_list:
        roi = edges[y_val:y_val+20, :]
        M_roi = cv2.moments(roi)
        if M_roi["m00"] != 0:
            cx = int(M_roi["m10"] / M_roi["m00"])
            cy = int(M_roi["m01"] / M_roi["m00"]) + y_val
            weighted_sum += cx * weight
            total_weight += weight
            cy_roi = cy

    # 차선 중심 인식 실패한 경우: angle = 90 고정
    if total_weight == 0:
        print("❌ 차선 인식 실패 → 90도 고정")
        return ANGLE_CENTER

    # 차선 중심 인식 성공한 경우: PID 보정 및 angle 계산
    cx_weighted = int(weighted_sum / total_weight)
    smooth_cx = int(pid.update(prev_cx or cx_weighted, cx_weighted))
    prev_cx = smooth_cx

    error = smooth_cx - 320  # 이미지 중심 기준 오차
    offset_ratio = np.clip(error / 160, -1, 1)
    angle = int(ANGLE_CENTER - offset_ratio * MAX_ANGLE_OFFSET)
    angle = np.clip(angle, 45, 135)

    #  디버깅 출력
    print(f"▶ 조향 계산 정보 | weighted_cx={cx_weighted}, smoothed_cx={smooth_cx}, error={error}, angle={angle}")

    return angle



    # if error < -20:
    #     return angle
    # elif error > 20:
    #     return angle
    # else:
    #     return angle
