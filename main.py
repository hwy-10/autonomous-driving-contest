# main loop
import motor_control as motor # motor_control 모듈을 import하여 GPIO 초기화 및 모터 제어 기능을 부름
import utills # 디버깅용


try:
    while True:
        # Flask 웹서버 안열어도 되고, # 카메라 입력 필요없음
        # 여기에 카메라 입력을 받아서 처리하는 코드 작성
        # openCV 인자를 받음 A가 만들어라
        # CNN 인자를 받음 B가 만들어라
        # if CNN 인자 == "정지해야 하는 상황" : motor.stop_motor() 실행
        # else // do_nothing
        # speed와 steering_angle을 계산하는 로직 작성
    
        """switch(speed, steering_angle)"""
        # case 전진 : 
        motor.front_forward.motor_forward("""속도, 방향""") # 앞으로 전진
        # case 후진 : 
        motor.front_backward("""속도, 방향""") # 뒤로 후진

except KeyboardInterrupt:
    print("사용자 종료")

finally:
    motor.afb.stop_all()

# GIL이 공항게이트에서 티켓 검사함. 1개의 일만 입장 가능함. 그래서 다른 작업 멀티태스킹이 안됨
# GIL의 존재 의의 : 메모리 관리를 알아서 해줌. 오류 안남
# GIL이 없으면 메모리 관리를 직접 해야함. -> 그게 C, C++임
# 그래서 최적화하기 위해서 cython을 쓰든가, C++을 외부에서 하든가
# 계산을 C++로 하는게, numPy 같은 라이브러리
# 우리 코드에서 line_profile해서 느린 부분을 C++로 옮겨서 최적화
