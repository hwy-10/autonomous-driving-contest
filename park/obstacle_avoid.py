import motor_control as motor
import time
import afb
from vision.opencv_module import get_lane_center
from pid_controller import PIDController

def execute_avoid_and_realign():
    print("[AVOID] 회피 시작")

    # 1. 정지
    motor.front_stop()
    motor.rear_stop()
    time.sleep(0.3)

    # 2. 후진 + 조향
    motor.front_backward(150, 135)
    motor.rear_backward(150, 135)
    time.sleep(0.6)

    # 3. 전진 + 같은 조향
    motor.front_forward(150, 135)
    motor.rear_forward(150, 135)
    time.sleep(0.6)

    # 4. PID 기반 조향 복귀
    pid = PIDController(Kp=0.3, Ki=0.0, Kd=0.05)
    print("[REALIGN] PID 복귀 시작")

    for _ in range(15):  # 15프레임 정도 보정 시도
        frame = afb.camera.get_image()
        lane_center = get_lane_center(frame)
        frame_center = frame.shape[1] // 2
        error = lane_center - frame_center

        control = pid.compute(error)  # 조향 보정값

        # 조향 각도 제한 (0~180)
        angle = int(90 - control)
        angle = max(45, min(135, angle))

        motor.front_forward(120, angle)
        motor.rear_forward(120, angle)

        if abs(error) < 10:
            print("[REALIGN] 복귀 완료")
            break

        time.sleep(0.1)

    # 5. 조향 복귀
    motor.front_forward(150, 90)
    motor.rear_forward(150, 90)
    print("[AVOID] 완료 후 직진 복귀")
