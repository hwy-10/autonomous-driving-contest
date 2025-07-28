import runtime # 초기화 등 runtime에 필요한 함수를 import
from runtime.config import * # Status 이용을 위한 import
import cv2
import motor_control as motor # motor_control 모듈을 import하여 GPIO 초기화 및 모터 제어 기능을 부름
import utills # 디버깅용
from vision.cv_module import get_cv_angle, image_preprocessing
from vision.CNN import get_cnn_status, decide_final_status
from runtime import gpio    # 추가
# import threading

# main을 위한 초기화 
status = Status.go # 초기 상태를 전진(go)로 설정
runtime.gpio.init() # GPIO 초기화 및 global.pi 설정
runtime.camera.init(640, 480, 30) # 카메라 초기화를 진행해줌
runtime.gpio.led() # 초기 led를 끈 상태로 시작

# threading.Thread(target=start_server, daemon=True).start() # Flask 서버를 백그라운드에서 실행

# 반복문: 차량 진행 상태 결정 
try:
    while True:
        frame = runtime.camera.get_image() # 카메라로부터 프레임을 가져옴
        frame_gray = image_preprocessing(frame)
        steering_angle =  get_cv_angle(frame_gray) # OpenCV로부터 조향 결정
        cnn_status = get_cnn_status(frame) # YOLO로부터 상태 결정

        if frame_gray.mean() >= brightness_threshold: runtime.gpio.led() # 터널에서 빠져나온다면, led를 다시 끈다
        else: runtime.gpio.led(True, True) # 어둡다면, led를 킨다.
        
        status, stop_count = decide_final_status(cnn_status) # status 결정 match문에 사용
        # update_state(status, steering_angle)   # Flask 서버에 상태 업데이트
        
        # 결정된 status와 steering_angle에 따라 차량 제어
        match status : 
            case Status.go : 
                motor.front_forward(180, steering_angle)
                motor.rear_forward(180, steering_angle) 
            case Status.left : 
                motor.front_forward(180, steering_angle)
                motor.rear_forward(180, steering_angle)
            case Status.right : 
                motor.front_forward(180, steering_angle)
                motor.rear_forward(180, steering_angle)
            # case Status.back :
            #    motor.front_backward(180)
            #    motor.rear_backward(180)
            case Status.stop :
                motor.front_stop()
                motor.rear_stop() 
            case Status.avoid:
                motor.avoid(frame_gray) # gray 처리가 된 코드를 받음
            case Status.accelerate:
                motor.front_forward(200, steering_angle)
                motor.rear_forward(200, steering_angle) 
            case Status.decelerate:
                motor.front_forward(150, steering_angle)
                motor.rear_forward(150, steering_angle)
                
        print("CNN 상태:", cnn_status)  # 디버깅용 출력 추가
        print("조향 각도:", steering_angle)
        # print("gpio.pi 핸들:", gpio.pi)

        # 강제 확인
        ### print("앞바퀴 forward 호출")
        motor.front_forward(180, steering_angle)

        ### print("뒷바퀴 forward 호출")
        motor.rear_forward(180, steering_angle)



except KeyboardInterrupt: 
    print("사용자 종료")

finally:
    runtime.gpio.stop_all()
    runtime.camera.release_camera()