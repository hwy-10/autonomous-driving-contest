# afb/camera.py

import cv2
import time
import sys
sys.path.append("/usr/lib/python3/dist-packages")  # Add system packages path
from picamera2 import Picamera2

_picam2 = None

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
    return _picam2.capture_array("main")  # Only grab the latest available frame


# Release and clean up the camera
def release_camera():
    global _picam2
    if _picam2 is not None:
        _picam2.stop()
        _picam2 = None