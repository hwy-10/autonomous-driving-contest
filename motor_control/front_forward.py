import lgpio
import atexit
from afb import gpio
from afb._gpio_pins import PINS # 핀 정의 

def front_forward(speed = 0, angle = 90):
    """
    Control motor direction and speed.
    :param motor_id: 1 (M1 on TB6612FNG)
    :param speed: -255 ~ +255
    :param angle: 0 ~ 180 
    """
    IN1, IN2, PWM = PINS.M1_IN1, PINS.M1_IN2, PINS.M1_PWM # TB6612FNG M1 핀 정의

    if abs(speed) > 0: # 속도 0이 아니면, 전진을 위한 모터 제어
        lgpio.gpio_write(gpio.pi, IN1, 1)
        lgpio.gpio_write(gpio.pi, IN2, 0)
    elif speed == 0: # 속도 0이면, 모터 정지 
        lgpio.gpio_write(gpio.pi, IN1, 0)
        lgpio.gpio_write(gpio.pi, IN2, 0)

    duty = min(abs(speed), 255) / 255 * 100.0
    lgpio.tx_pwm(gpio.pi, PWM, 1000, duty)

    gpio.servo(angle) # 서보 모터 각도 제어
"""
해당 코드에서는 lgpio 라이브러리를 사용하여 모터를 제어한다. 
speed를 통해 모터의 속도를 설정한다.
angle의 경우, afb/gpio.py에서 정의된 메소드를 사용하여 서보 모터의 각도를 제어한다.
"""