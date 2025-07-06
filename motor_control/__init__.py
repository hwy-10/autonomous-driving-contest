import afb
import time
from . import front_forward
from . import front_backward
from . import front_stop
from . import rear_forward
from . import rear_backward
from . import rear_stop

afb.gpio.init() # main.py에서 import motor_control을 통해 자동으로 GPIO 초기화