import lgpio
import atexit
from afb import gpio
from afb._gpio_pins import PINS # 핀 정의 

def rear_stop():
    IN1, IN2, PWM = PINS.M2_IN1, PINS.M2_IN2, PINS.M2_PWM # TB6612FNG M2 핀 정의
    lgpio.gpio_write(gpio.pi, IN1, 0)
    lgpio.gpio_write(gpio.pi, IN2, 0)

    lgpio.tx_pwm(gpio.pi, PWM, 1000, 0) # PWM 신호를 0으로 설정하여 모터 정지
"""
모터는 0 속도로 정지하고, 서보 모터는 현재 각도를 유지한다.
"""