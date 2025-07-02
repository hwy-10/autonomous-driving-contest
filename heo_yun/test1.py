import cv2
import numpy as np

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

# 1) BEV 변환 함수
def warp_image(image, src_pts, dst_size=(640, 480)):
    width, height = dst_size
    dst_pts = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype=np.float32)
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(image, M, dst_size)
    return warped, M

# 2) 중심선 추적 함수
def contour_centroids_by_row(binary_img, step=20):
    h, w = binary_img.shape
    overlay = cv2.cvtColor(binary_img, cv2.COLOR_GRAY2BGR)
    left_points, right_points, mid_points = [], [], []

    for y in range(h - step, 0, -step):
        roi = binary_img[y:y+step, :]
        contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        centers = []
        for cnt in contours:
            if cv2.contourArea(cnt) < 20:
                continue
            M = cv2.moments(cnt)
            if M['m00'] > 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00']) + y
                centers.append((cx, cy))
                cv2.circle(overlay, (cx, cy), 2, (255, 0, 255), -1)

        if not centers:
            continue

        mid = w // 2
        lefts = [pt for pt in centers if pt[0] < mid]
        rights = [pt for pt in centers if pt[0] >= mid]

        if not lefts or not rights:
            continue

        lx = int(np.mean([pt[0] for pt in lefts]))
        ly = int(np.mean([pt[1] for pt in lefts]))
        rx = int(np.mean([pt[0] for pt in rights]))
        ry = int(np.mean([pt[1] for pt in rights]))

        mx = (lx + rx) // 2
        my = (ly + ry) // 2

        if mid_points:
            prev_mx = mid_points[-1][0]
            if abs(mx - prev_mx) > 20:
                mx = prev_mx

        mid_points.append((mx, my))
        left_points.append((lx, ly))
        right_points.append((rx, ry))

        cv2.circle(overlay, (lx, ly), 3, (0, 0, 255), -1)
        cv2.circle(overlay, (rx, ry), 3, (255, 0, 0), -1)
        cv2.circle(overlay, (mx, my), 4, (0, 255, 255), -1)

    for i in range(len(mid_points) - 1):
        cv2.line(overlay, mid_points[i], mid_points[i+1], (0, 255, 0), 2)

    return overlay

# 메인 함수
def main():
    src_pts = np.array([[170, 290], [440, 290], [564, 390], [80, 390]], dtype=np.float32)
    cap = cv2.VideoCapture('vod_test.mp4')
    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = int(3000 / fps) if fps > 0 else 30

    pid = PIDController(kp=0.4, ki=0.0, kd=0.05)
    prev_cx = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, 480))
        cv2.imshow('Original Frame', frame)

        warped, M = warp_image(frame, src_pts)
        cv2.imshow('Warped BEV Raw', warped)

        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 1.5)
        edges = cv2.Canny(blur, 40, 120)
        cv2.imshow('Canny Edges', edges)

        # 여러 y값에서 무게중심 계산 + 가중평균
        target_y_list = [(370, 10), (360, 5), (350, 3), (340, 2)] # 총 20으로 가중치 계산
        weighted_sum = 0
        total_weight = 0
        cy_roi = None

        for y_val, weight in target_y_list:
            roi = edges[y_val:y_val+20, :]
            M_roi = cv2.moments(roi)
            if M_roi["m00"] != 0:
                cx = int(M_roi["m10"] / M_roi["m00"])
                cy = int(M_roi["m01"] / M_roi["m00"]) + y_val
                weighted_sum += cx * weight
                total_weight += weight
                cy_roi = cy  # 마지막 y값 기준으로 출력 위치 설정

        if total_weight == 0:
            continue  # 중심점이 없으면 프레임 건너뜀

        cx_weighted = int(weighted_sum / total_weight)

        if prev_cx is None:
            smooth_cx = cx_weighted
        else:
            smooth_cx = int(pid.update(prev_cx, cx_weighted))
        prev_cx = smooth_cx

        # 시각화
        cv2.circle(frame, (smooth_cx, cy_roi), 5, (0, 255, 0), -1)
        cv2.putText(frame, f"Smoothed CX: {smooth_cx}", (smooth_cx + 10, cy_roi - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        overlay = contour_centroids_by_row(edges)
        cv2.imshow('Contour Midline Overlay', overlay)

        invM = np.linalg.inv(M)
        unwarp = cv2.warpPerspective(overlay, invM, (640, 480))
        orig_overlay = cv2.addWeighted(frame, 0.7, unwarp, 1.0, 0)
        cv2.imshow('Original + Midline Overlay', orig_overlay)

        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()