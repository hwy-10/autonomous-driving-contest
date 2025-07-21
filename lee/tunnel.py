import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

# 릴레이 제어용 GPIO 핀 설정
RELAY_PIN = 17

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # 초기 상태는 꺼짐

# 밝기 임계값 및 시간 조건
LUX_THRESHOLD = 50
DARK_DURATION_THRESHOLD = 2.0
BRIGHT_DURATION_THRESHOLD = 2.0

dark_start_time = None
bright_start_time = None
in_tunnel = False
headlight_on = False

def calculate_brightness(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return np.mean(gray)

def turn_on_headlight():
    global headlight_on
    if not headlight_on:
        headlight_on = True
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        print("[전조등 켜짐]")

def turn_off_headlight():
    global headlight_on
    if headlight_on:
        headlight_on = False
        GPIO.output(RELAY_PIN, GPIO.LOW)
        print("[전조등 꺼짐]")

# 카메라 열기 (PiCamera는 특별한 설정 필요, 일반 USB카메라는 그대로 사용)
cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()
        brightness = calculate_brightness(frame)

        # 밝기 로직
        if brightness < LUX_THRESHOLD:
            bright_start_time = None
            if dark_start_time is None:
                dark_start_time = current_time
            elif (current_time - dark_start_time) >= DARK_DURATION_THRESHOLD and not in_tunnel:
                in_tunnel = True
                turn_on_headlight()
        else:
            dark_start_time = None
            if in_tunnel:
                if bright_start_time is None:
                    bright_start_time = current_time
                elif (current_time - bright_start_time) >= BRIGHT_DURATION_THRESHOLD:
                    in_tunnel = False
                    turn_off_headlight()
            else:
                bright_start_time = None

        # 밝기 시각화 (원한다면 디스플레이 연결 필요)
        print(f"Brightness: {brightness:.2f} | Headlight: {'ON' if headlight_on else 'OFF'}")
        
        # q 키 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()
