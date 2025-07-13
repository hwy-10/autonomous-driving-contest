import cv2
import numpy as np
import os
import glob

# 1. 이미지 폴더 경로 설정
img_folder = r'C:\Users\user\Desktop\git-clones\autonomous-driving-contest\media_file\lane_image'
img_paths = glob.glob(os.path.join(img_folder, '*.jpg'))

# 2. 차선 마스킹 함수 (ROI 포함)
def extract_lane(img):
    # 크기 표준화
    img = cv2.resize(img, (640, 480))

    # 하단 ROI 설정 (예: 아래쪽 1/2만)
    roi = img[240:480, :]

    # HSV 변환
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # 흰색 차선 범위 (조절 가능)
    lower_white = np.array([0, 0, 180])
    upper_white = np.array([180, 40, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # 마스크를 원본 크기로 복원
    full_mask = np.zeros((480, 640), dtype=np.uint8)
    full_mask[240:480, :] = mask

    # 마스크 적용 (차선 추출)
    lane_only = cv2.bitwise_and(img, img, mask=full_mask)

    return img, full_mask, lane_only

# 3. 이미지 반복 처리 및 출력
for path in img_paths:
    img = cv2.imread(path)
    if img is None:
        print(f"⚠️ 이미지 로드 실패: {path}")
        continue

    original, mask, lane_img = extract_lane(img)

    # 마스크를 3채널로 변환
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # 화면에 나란히 출력
    combined = np.hstack((original, mask_bgr, lane_img))
    cv2.imshow('Original | Mask | Extracted Lane', combined)

    key = cv2.waitKey(300)
    if key == 27:  # ESC 눌러서 중지 가능
        break

cv2.destroyAllWindows()
