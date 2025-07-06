## motor_id == 2인 경우가 rear motor control

import lgpio
import atexit
import afb
from afb._gpio_pins import PINS

# Create global lgpio instance
pi = lgpio.gpiochip_open(0)
atexit.register(lambda: stop_all()) # 종료 루틴


def motor(speed = 0, inverse = 1, motor_id = 1):
    """
    Control motor direction and speed.
    :param speed: -255 ~ +255
    """
    if motor_id == 1:
        IN1, IN2, PWM = PINS.M1_IN1, PINS.M1_IN2, PINS.M1_PWM
    elif motor_id == 2:
        IN1, IN2, PWM = PINS.M2_IN1, PINS.M2_IN2, PINS.M2_PWM
    else:
        raise ValueError("motor_id must be 1 or 2")

    if speed * inverse > 0:
        lgpio.gpio_write(pi, IN1, 1)
        lgpio.gpio_write(pi, IN2, 0)
    elif speed * inverse < 0:
        lgpio.gpio_write(pi, IN1, 0)
        lgpio.gpio_write(pi, IN2, 1)
    else:
        lgpio.gpio_write(pi, IN1, 0)
        lgpio.gpio_write(pi, IN2, 0)

    duty = min(abs(speed), 255) / 255 * 100.0
    lgpio.tx_pwm(pi, PWM, 1000, duty)