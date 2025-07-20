import cv2
import numpy as np

# 파라미터
WIDTH, HEIGHT = 640, 480
CENTER_X = WIDTH // 2
AREA_THRESHOLD = 1000
ROI_VERT_START = HEIGHT // 2

# HSV 범위 (흰색 차선만)
WHITE_LOWER = np.array([0, 0, 200])
WHITE_UPPER = np.array([180, 30, 255])

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))   # 모폴로지 연산용 커널
last_center = None  # 무게중심의 스무딩(이동평균)을 위한 이전값 저장

def preprocess(image):
    # ROI: 화면 하단부만 사용
    roi = image[ROI_VERT_START:, :]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, WHITE_LOWER, WHITE_UPPER)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask

def find_center(mask):
    edges = cv2.Canny(mask, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid = [cnt for cnt in contours if cv2.contourArea(cnt) > AREA_THRESHOLD]
    if not valid:
        return None
    largest = max(valid, key=cv2.contourArea)
    M = cv2.moments(largest)
    if M['m00'] == 0:
        return None
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00']) + ROI_VERT_START  # 원래 프레임 기준으로 변환
    return cx, cy

def decide_dir(cx):
    if cx is None:
        return "정지"
    err = CENTER_X - cx
    if abs(err) < 20:
        return "직진"
    return "좌회전" if err > 0 else "우회전"

def process(frame):
    mask = preprocess(frame)
    center = find_center(mask)
    direction = decide_dir(center[0] if center else None)

    # 스무딩: 이동평균
    global last_center
    if center:
        sm = int(0.7 * (last_center or center[0]) + 0.3 * center[0])
        last_center = sm
    else:
        sm = last_center

    # 시각화
    if sm:
        cv2.circle(frame, (sm, HEIGHT-10), 5, (0,255,0), -1)
    cv2.line(frame, (CENTER_X, ROI_VERT_START), (CENTER_X, HEIGHT), (255,0,0), 2)
    cv2.putText(frame, direction, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    return frame, direction

if __name__ == "__main__":
    # video_path 에 파일 경로 넣거나 0 으로 웹캠 사용
    video_path = 0
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        result, direction = process(frame)
        cv2.imshow("LanePilot", result)

        # 'q' 키 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
