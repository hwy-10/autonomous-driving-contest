import lgpio
import atexit
from afb import gpio
from afb._gpio_pins import PINS # 핀 정의 

def rear_backward(speed = 0, angle = 90):
    """
    Control motor direction and speed.
    :param motor_id: 2 (M2 on TB6612FNG)
    :param speed: -255 ~ +255
    :param angle: 0 ~ 180 
    """
    IN1, IN2, PWM = PINS.M2_IN1, PINS.M2_IN2, PINS.M2_PWM # TB6612FNG M2 핀 정의

    if abs(speed) > 0: # 속도 0이 아니면, 후진을 위한 모터 제어
        lgpio.gpio_write(gpio.pi, IN1, 0)
        lgpio.gpio_write(gpio.pi, IN2, 1)
    elif speed == 0: # 속도 0이면, 모터 정지 
        lgpio.gpio_write(gpio.pi, IN1, 0)
        lgpio.gpio_write(gpio.pi, IN2, 0)

    duty = min(abs(speed), 255) / 255 * 100.0
    lgpio.tx_pwm(gpio.pi, PWM, 1000, duty)

    gpio.servo(angle) # 서보모터 제어