import cv2
import numpy as np

def nothing(x):
    pass

# 창 생성
cv2.namedWindow("Trackbars")

# 트랙바 생성 (Hue 0~179, Sat/Val 0~255)
cv2.createTrackbar("H Lower", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("H Upper", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("S Lower", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("S Upper", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("V Lower", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("V Upper", "Trackbars", 255, 255, nothing)

# 카메라 또는 이미지로 테스트
img = cv2.imread("logo.jpg")  # 또는 cap.read() 사용

while True:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 트랙바에서 값 읽기
    hL = cv2.getTrackbarPos("H Lower", "Trackbars")
    hU = cv2.getTrackbarPos("H Upper", "Trackbars")
    sL = cv2.getTrackbarPos("S Lower", "Trackbars")
    sU = cv2.getTrackbarPos("S Upper", "Trackbars")
    vL = cv2.getTrackbarPos("V Lower", "Trackbars")
    vU = cv2.getTrackbarPos("V Upper", "Trackbars")

    lower = np.array([hL, sL, vL])
    upper = np.array([hU, sU, vU])

    # 마스크 생성
    mask = cv2.inRange(hsv, lower, upper)
    result = cv2.bitwise_and(img, img, mask=mask)

    cv2.imshow("Mask", mask)
    cv2.imshow("Result", result)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC키로 종료
        break

cv2.destroyAllWindows()
