import os
import cv2
import numpy as np
import time
import afb
import sys
sys.path.append("/usr/lib/python3/dist-packages")  # Add system packages path
from picamera2 import Picamera2

_picam2 = None

# 고정 파라미터 설정
THRESHOLD_VAL = 160
CANNY_LOW = 20
CANNY_HIGH = 150
HSV_LOWER = np.array([0, 0, 200])
HSV_UPPER = np.array([180, 50, 255])
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

def init(width=640, height=480, framerate=30): # 해상도를 640x480으로 설정하고 fps를 30으로 설정
    global _picam2
    if _picam2 is not None:
        _picam2.stop()
    _picam2 = Picamera2()  # 인스턴스를 생성
    _picam2.configure(
        _picam2.create_preview_configuration(
            main={"size": (width, height)}, # 메인 카메라 크기 설정
            controls={"FrameDurationLimits": (int(1e6 // framerate), int(1e6 // framerate))} # 30fps 설정
        )
    )
    _picam2.start()
    time.sleep(1)  # Allow camera to warm up

def get_image():
    if _picam2 is None:
        raise RuntimeError("Camera not initialized. Call init() first.")
    return _picam2.capture_array("main")  # Only grab the latest available frame <class 'numpy.ndarray'>

# Release and clean up the camera : 프로그램 종료 시 카메라를 정리(clean-up)할 때 사용하는 함수
def release_camera():
    global _picam2
    if _picam2 is not None:
        _picam2.stop()
        _picam2 = None

def hsv_mask(image) : 
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv_mask = cv2.inRange(hsv, HSV_LOWER, HSV_UPPER)
    hsv_result = cv2.bitwise_and(image, image, mask=hsv_mask)

def gray_mask(image) : 
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    

def filtering(image) :
    closing = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
    opening = cv2.erode(opening, kernel, iterations=1)
    return opening

def binary(image) :
    _, binary = cv2.threshold(image, THRESHOLD_VAL, 255, cv2.THRESH_BINARY)
    return binary

def contour(image) : 
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(image)
    cv2.drawContours(filled, contours, -1, 255, thickness=cv2.FILLED)
    return 

def canny(image) :

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(binary)
    cv2.drawContours(filled, contours, -1, 255, thickness=cv2.FILLED)
    
    edges = cv2.Canny(filled, CANNY_LOW, CANNY_HIGH)