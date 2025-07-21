# main loop
import afb
import motor_control as motor # motor_control 모듈을 import하여 GPIO 초기화 및 모터 제어 기능을 부름
import utills # 디버깅용
import random
import camera 
from enum import Enum

class Status(Enum) :
    go = 0
    left = 1
    right = 2
    back = 3
    stop = 4
    avoid = 5
    accelerate = 6
    decelerate = 7

PRIORITY_RULES = [
        ("cnn", Status.stop),
        ("cnn", Status.avoid),
        ("cnn", Status.accelerate),
        ("cnn", Status.decelerate),
        ("both", Status.go),
        ("both", Status.left),
        ("both", Status.right),
        ("cv", Status.back)
    ]

# back은 openCV로만 구현 -> 이후 CNN으로도 구현해야 한다면, 구현하기
# CNN: go, left, right, stop, avoid, accel, decel 총 7개 상태

status = Status.go # 초기 상태를 전진(go)로 설정
afb.gpio.init() # GPIO 초기화 및 global.pi 설정

stop_count = 0
stop_threshold = 3

afb.camera.init(640, 480, 30) # 카메라 초기화를 진행해줌


def decide_final_status(cv_status, cnn_status): # Status class, stop_count 반환
    # 1. stop 누적 판단 따로 처리
    if cnn_status == Status.stop:
        stop_count += 1
        if stop_count >= stop_threshold:
            return Status.stop, stop_count
        else:
            return Status.decelerate, stop_count # 일단 stop 시그널을 보냈을 때, 감속하는 방식으로

    stop_count = 0

    # 2. 우선순위 순회
    for source, rule_status in PRIORITY_RULES:
        if source == "cnn" and cnn_status == rule_status:
            return rule_status, stop_count
        if source == "cv" and cv_status == rule_status:
            return rule_status, stop_count
        if source == "both" and cnn_status == rule_status and cv_status == rule_status: # both일 때, 가중치를 두기
            return rule_status, stop_count

    return Status.go, stop_count


try:
    while True:
        # Flask 웹서버 안열어도 되고, # 카메라 입력 필요없음
        # 여기에 카메라 입력을 받아서 처리하는 코드 작성
        # openCV 인자를 받음 A가 만들어라
        # CNN 인자를 받음 B가 만들어라
        # 메소드 def decide_final_status를 통해 status 결정하기
        cv_status =  """vision/openCV로 받는 데이터 : return speed, steering_angle"""
        cnn_status = """"vison/CNN로 받는 데이터 return speed,steering_angle, status""" 
        status, stop_count = decide_final_status(cv_status, cnn_status) # status 결정 match문에 사용
        



# 결정된 status로부터 차량을 제어하는 logic -> 구체적인 코드만 작성하면 됨
        match status : 
            case Status.go : 
                motor.front_forward()
                motor.rear_forward()
            case Status.left : 
                """ left code """
            case Status.right : 
                """ right code """
            case Status.back :
                motor.front_backward()
                motor.rear_backward()
            case Status.stop :
                motor.front_stop()
                motor.rear_stop() 
            case Status.avoid:
                """ avoid code """
            case Status.accelerate:
                """ accel code """
            case Status.decelerate:
                """ decel code """




except KeyboardInterrupt: # 
    print("사용자 종료")

finally:
    afb.gpio.stop_all()