import afb
from .front_forward import *
from .front_backward import *
from .front_stop import *
from .rear_forward import *
from .rear_backward import *
from .rear_stop import *

afb.gpio.init() # main.py에서 import motor_control을 통해 자동으로 GPIO 초기화