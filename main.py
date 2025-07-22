import runtime # 초기화 등 runtime에 필요한 함수를 import
from runtime.status import * # Status 이용을 위한 import
import cv2
import motor_control as motor # motor_control 모듈을 import하여 GPIO 초기화 및 모터 제어 기능을 부름
import utills # 디버깅용
from vision.cv_module import get_cv_status
from vision.CNN import get_cnn_status

# main을 위한 초기화 
status = Status.go # 초기 상태를 전진(go)로 설정
runtime.gpio.init() # GPIO 초기화 및 global.pi 설정
runtime.camera.init(640, 480, 30) # 카메라 초기화를 진행해줌

# 반복문: 차량 진행 상태 결정 
try:
    while True:
        frame = runtime.camera.get_image() # 카메라로부터 프레임을 가져옴
        cv_status, steering_angle =  get_cv_status(frame) # OpenCV로부터 상태를 결정
        cnn_status = get_cnn_status(frame) # class Status 객체를 받음
        status, stop_count, steering_angle = decide_final_status(cv_status, cnn_status) # status 결정 match문에 사용
        
        # 결정된 status와 steering_angle에 따라 차량 제어
        match status : 
            case Status.go : 
                motor.front_forward(180) # speed, angle = 90
                motor.rear_forward(180) 
            case Status.left : 
                motor.front_forward(180, steering_angle)
                motor.rear_forward(180, steering_angle)
            case Status.right : 
                motor.front_forward(180, steering_angle)
                motor.rear_forward(180, steering_angle)
            case Status.back :
                motor.front_backward(180)
                motor.rear_backward(180)
            case Status.stop :
                motor.front_stop()
                motor.rear_stop() 
            case Status.avoid:
                motor.avoid()
            case Status.accelerate:
                motor.front_forward(200, steering_angle)
                motor.rear_forward(200, steering_angle) 
            case Status.decelerate:
                motor.front_forward(150, steering_angle)
                motor.rear_forward(150, steering_angle)

except KeyboardInterrupt: 
    print("사용자 종료")

finally:
    runtime.gpio.stop_all()
    runtime.camera.release_camera()