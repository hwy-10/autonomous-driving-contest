import cv2
import numpy as np
import math

def warp_image(image, src_pts, dst_size=(640, 480)):
    width, height = dst_size
    dst_pts = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(image, M, dst_size)
    return warped, M

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
    image_path = "pict/frame_20250630_124117.jpg"
    src_pts = np.array([[170, 290], [440, 290], [564, 390], [80, 390]], dtype=np.float32)

    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Failed to load image: {image_path}")
        return

    frame = cv2.resize(frame, (640, 480))
    warped, M = warp_image(frame, src_pts)
    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 1.5)
    edges = cv2.Canny(blur, 40, 120)

    # 단일 y = 380 ROI에서 중심선 계산
    y_val = 380
    roi = edges[y_val:y_val+20, :]
    M_roi = cv2.moments(roi)

    if M_roi["m00"] == 0:
        print("라인을 찾을 수 없습니다.")
        return

    cx = int(M_roi["m10"] / M_roi["m00"])
    cy = int(M_roi["m01"] / M_roi["m00"]) + y_val

    # PID 제거 → 바로 cx 사용
    final_direction = get_direction_from_cx(cx, 640)

    # --- 시각화 ---
    result_frame = frame.copy()
    color = (0, 255, 0)

    # BEV 좌표 점 시각화
    for i, pt in enumerate(src_pts):
        pt_int = tuple(int(v) for v in pt)
        cv2.circle(result_frame, pt_int, 5, (255, 0, 255), -1)  # 보라색 점
        cv2.putText(result_frame, f"P{i+1}: {pt_int}", (pt_int[0] + 5, pt_int[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)

    # 중심선 결과 시각화
    cv2.circle(result_frame, (cx, cy), 6, color, -1)
    cv2.putText(result_frame, f"Direction: {final_direction}", (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    h, w, _ = result_frame.shape
    start_point = (w // 2, h - 50)
    if final_direction == "Straight":
        end_point = (start_point[0], start_point[1] - 100)
    elif final_direction == "Left":
        end_point = (start_point[0] - 60, start_point[1] - 100)
    elif final_direction == "Right":
        end_point = (start_point[0] + 60, start_point[1] - 100)
    else:
        end_point = (start_point[0], start_point[1])

    cv2.arrowedLine(result_frame, start_point, end_point, color, 4, tipLength=0.3)
    cv2.putText(result_frame, "Planned Path", (start_point[0] - 50, start_point[1] + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    cv2.imshow("Single-line Canny Direction + Points (No PID)", result_frame)
    print("Press any key to exit...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
