# main loop
import afb
import motor_control as motor # motor_control 모듈을 import하여 GPIO 초기화 및 모터 제어 기능을 부름
import utills # 디버깅용
import random
from enum import Enum

class Status(Enum) :
    go = 1
    back = 2
    stop = 3

status = Status.go # 초기 상태를 전진(go)로 설정
afb.gpio.init() # GPIO 초기화 및 global.pi 설정

stop_count = 0
stop_threshold = 3

try:
    while True:
        # Flask 웹서버 안열어도 되고, # 카메라 입력 필요없음
        # 여기에 카메라 입력을 받아서 처리하는 코드 작성
        # openCV 인자를 받음 A가 만들어라
        # CNN 인자를 받음 B가 만들어라
        openCV_speed, openCV_angle, openCV_status = """vision/openCV로 받는 데이터 : return speed, steering_angle"""
        CNN_speed, CNN_angle, CNN_status = """"vison/CNN로 받는 데이터 return speed,steering_angle, status""" 
        
        if CNN_status == Status.stop:
            stop_count += 1
            if stop_count >= stop_threshold:
                status = Status.stop
        # match 실행을 위해 continue하지 않음
        # 그대로 내려가서 stop 명령 실행
            else:
                continue  # 아직 임계치 미만이면 다음 루프로 넘어감

        elif openCV_status == Status.go and CNN_status == Status.go : 
            status = Status.go
            stop_count = 0
        else :  # 이후에 더 go, back, stop 상태 세분화할 것
            stop_count = 0

        match status : 
            case Status.stop :
                motor.front_stop()
                motor.rear_stop() 
            case Status.go :
                motor.front_forward()
                motor.rear_forward()
            case Status.back :
                motor.front_backward()
                motor.rear_backward()

except KeyboardInterrupt:
    print("사용자 종료")

finally:
    afb.gpio.stop_all()