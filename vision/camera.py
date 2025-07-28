import os
import cv2
import numpy as np
import time
# import afb
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