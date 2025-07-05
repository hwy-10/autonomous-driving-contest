import cv2
import numpy as np
import math

# --- PID Controller ---
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

# --- 벡터 기반 방향 판단 ---
def get_direction_by_angle(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    height, width = edges.shape
    roi = edges[int(height/2):, :]
    lines = cv2.HoughLinesP(roi, 1, np.pi/180, 50, minLineLength=50, maxLineGap=100)
    if lines is None:
        return "Unknown"
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        dx = x2 - x1
        dy = y1 - y2
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad) % 180
        angles.append(angle_deg)
    avg_angle = np.mean(angles)
    if 75 <= avg_angle <= 105:
        return "Straight"
    elif avg_angle < 75:
        return "Right"
    else:
        return "Left"

# --- BEV 변환 ---
def warp_image(image, src_pts, dst_size=(640, 480)):
    width, height = dst_size
    dst_pts = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(image, M, dst_size)
    return warped, M

# --- 중심선 방향 판단 (Canny 기반) ---
def get_direction_from_cx(cx, frame_width):
    mid = frame_width // 2
    error = cx - mid
    if abs(error) < 20:
        return "Straight"
    elif error < -20:
        return "Left"
    else:
        return "Right"

# --- Main ---
def main():
    src_pts = np.array([[170, 290], [440, 290], [564, 390], [80, 390]], dtype=np.float32)
    cap = cv2.VideoCapture("media_file/vod_test.mp4")
    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = int(1000 / fps) if fps > 0 else 30
    pid = PIDController(kp=0.5, ki=0.0, kd=0.05)
    prev_cx = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (640, 480))
        warped, M = warp_image(frame, src_pts)
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 1.5)
        edges = cv2.Canny(blur, 40, 120)

        # --- 중심선 가중 평균 계산 ---
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
        if total_weight == 0:
            continue
        cx_weighted = int(weighted_sum / total_weight)
        smooth_cx = int(pid.update(prev_cx or cx_weighted, cx_weighted))
        prev_cx = smooth_cx

        # --- 방향 판단 ---
        canny_direction = get_direction_from_cx(smooth_cx, 640)
        vector_direction = get_direction_by_angle(frame)
        
        if canny_direction == vector_direction:
            final_direction = canny_direction
            agreement = True
        else:
            final_direction = "Straight"  # 충돌 시 무조건 직진
            agreement = False

        # --- 시각화 ---
        result_frame = frame.copy()
        color = (0, 255, 0) if agreement else (0, 0, 255)
        cv2.circle(result_frame, (smooth_cx, cy_roi), 6, color, -1)
        cv2.putText(result_frame, f"Canny: {canny_direction}", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(result_frame, f"Vector: {vector_direction}", (30, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(result_frame, f"Final: {final_direction}", (30, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)

        # --- 가상 주행 경로 그리기 ---
        h, w, _ = result_frame.shape
        start_point = (w // 2, h - 50)

        if final_direction == "Straight":
            end_point = (start_point[0], start_point[1] - 100)
        elif final_direction == "Left":
            end_point = (start_point[0] - 60, start_point[1] - 100)
        elif final_direction == "Right":
            end_point = (start_point[0] + 60, start_point[1] - 100)
        else:
            end_point = (start_point[0], start_point[1])  # no movement

        cv2.arrowedLine(result_frame, start_point, end_point,
                        color, 4, tipLength=0.3)
        cv2.putText(result_frame, "Planned Path", (start_point[0] - 50, start_point[1] + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        cv2.imshow("Direction Decision Fusion", result_frame)

        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
