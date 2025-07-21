import afb
import motor_control as motor # motor_control 모듈을 import하여 GPIO 초기화 및 모터 제어 기능을 부름
import utills # 디버깅용
import random
import camera 
from enum import Enum
from config import *

import time
from camera import LanePilot
from vision import CNN


status = Status.go # 초기 상태를 전진(go)로 설정

afb.gpio.init() # GPIO 초기화 및 global.pi 설정
afb.camera.init(640, 480, 30) # 카메라 초기화를 진행해줌

try:
    while True:
        # Flask 웹서버 안열어도 되고, # 카메라 입력 필요없음
        # 여기에 카메라 입력을 받아서 처리하는 코드 작성
        # openCV 인자를 받음 A가 만들어라
        # CNN 인자를 받음 B가 만들어라
        cv_status =  """vision/openCV로 받는 데이터 : return speed, steering_angle"""
        cnn_status = """"vison/CNN로 받는 데이터 return speed,steering_angle, status""" 
        status, stop_count = decide_final_status(cv_status, cnn_status) # status 결정 match문에 사용

# 결정된 status로부터 차량을 제어하는 logic -> 구체적인 코드만 작성하면 됨
        match status : 
            case Status.go : 
                motor.front_forward(180) # speed, angle = 90
                motor.rear_forward(180) # speed, angle = 90
            case Status.left : 
                motor.front_forward(180, 45) # speed, angle = 45 // angle의 경우 위에서 따로 정의해서 PID 제어할것
                motor.rear_forward(180, 45)
            case Status.right : 
                motor.front_forward(180, 135)
                motor.rear_forward(180, 135)
            case Status.back :
                motor.front_backward(180) # speed, angle = 90
                motor.rear_backward(180) # speed, angle = 90
            case Status.stop :
                motor.front_stop()
                motor.rear_stop() 
            case Status.avoid:
                #------------------------------------------------------------
                 # 1) 감속(decelerate 속도) 유지
                speed = 150

                # 2) 장애물 위치 파악 (CNN)
                frame = camera.get_image()
                detections = CNN.detect_objects(frame)
                obstacle = next((bbox for lbl, bbox in detections if lbl == CNN.YOLO_label.car), None)
                obj_cx = LanePilot.CENTER_X if obstacle is None else obstacle[0] + obstacle[2] // 2

                # 3) 장애물 반대 방향으로 회피 각도 계산
                if obj_cx < LanePilot.CENTER_X:
                    avoid_angle = 135  # 장애물이 왼쪽 → 우회전
                else:
                    avoid_angle = 45   # 장애물이 오른쪽 → 좌회전

                # 4) 원래 위치(직진 90°)에서 벗어난 만큼 보정 각도 계산
                #    offset = avoid_angle - 90, recover_angle = 90 - offset
                offset = avoid_angle - 90
                recover_angle = 90 - offset

                # 5) 1차 회피: 감속 + 조향
                motor.front_forward(speed, avoid_angle)
                motor.rear_forward(speed, avoid_angle)
                time.sleep(0.5)

                # 6) 2차 복귀: 감속 + 역조향
                motor.front_forward(speed, recover_angle)
                motor.rear_forward(speed, recover_angle)
                time.sleep(0.5)
                #------------------------------------------------------------
            case Status.accelerate:
                motor.front_forward(200) # speed up -> 속도는 이후 조정
                motor.rear_forward(200) 
            case Status.decelerate:
                motor.front_forward(150) # speed down -> 속도는 이후 조정
                motor.rear_forward(150)

except KeyboardInterrupt: # 
    print("사용자 종료")

finally:
    afb.gpio.stop_all()