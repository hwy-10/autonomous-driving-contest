import motor_control as motor # motor_control 모듈을 import하여 GPIO 초기화 및 모터 제어 기능을 부름
import time

class Obstacle:
    def __init__(self, label, priority = 0):
        self.label = label
        self.priority = priority
        
    def action(self):
        """상황에 따른 기본 행동 정의"""
        return f"[{self.label}] 기본 행동 없음"

class TurnLeft(Obstacle):
    def __init__(self):
        super().__init__("좌회전", priority=1)

    def action(self):
        print("[Action] 좌회전 실행")
        motor.front_forward(150, 120)   # 속도 150, 각도 120으로 좌회전
        motor.rear_forward(150, 120)    # 속도 150, 각도 120으로 좌회전
        time.sleep(0.6)
        
class TurnRight(Obstacle):
    def __init__(self):
        super().__init__("우회전", priority=1)

    def action(self):
        print("[Action] 우회전 실행")
        motor.front_forward(150, 60)    # 속도 150, 각도 60으로 우회전
        motor.rear_forward(150, 60)     # 속도 150, 각도 60으로 우회전
        time.sleep(0.6)


class Uphill(Obstacle):
    def __init__(self, direction="up"):
        super().__init__("언덕", priority=2)
        self.direction = direction

    def action(self):
        print(f"[Action] 언덕 {self.direction} 실행")
        speed = 200 if self.direction == "up" else 100
        motor.front_forward(speed, 90)  # 언덕 오를 때는 속도를 높임
        motor.rear_forward(speed, 90)


class Tunnel(Obstacle):
    def __init__(self):
        super().__init__("터널", priority=1)

    def action(self):
        print("[Action] 터널 진입 - 전조덩 켜기 + 속도 유지")
        motor.front_forward(150, 90)  # 속도 150, 각도 90으로 직진
        motor.rear_forward(150, 90)   # 속도 150, 각도 90으로 직진


class DynamicObstacle(Obstacle):
    def __init__(self, label, priority=3):
        super().__init__("동적장애물", priority = 5)
        self.direction = direction # 향후 좌, 우 확장
        
    def action(self):
        print("[Action] 동적 장애물 감지 -> 정지")
        motor.front_stop()
        motor.rear_stop()
        

class TrafficLight(Obstacle):
    def __init__(self, color):
        super().__init__("신호등", priority=4)
        self.color = color  # "red", "green", "yellow"

    def action(self):
        if self.color == "red":
            motor.front_stop()
            motor.rear_stop()
        elif self.color == "green":
            motor.front_forward(150, 90)
            motor.rear_forward(150, 90)
        elif self.color == "yellow":
            motor.front_forward(100, 90)
            motor.rear_forward(100, 90)
        else:
            return "알 수 없는 신호등 색상"
        
class StaticCar(Obstacle):
    def __init__(self, distance=None):
        super().__init__("정적장애물", priority=3)
        self.distance = distance # 거리 정보 활용 가능 (거리 센서 값 (cm))

    def action(self):
        if self.distance is not None and self.distance < 30:
            print("[Action] 정적 장애물 회피 동작 시작")
            
            # 정지
            motor.front_stop()
            motor.rear_stop()
            time.sleep(0.3)
            
            # 후진 + 조향
            motor.front_backward(150, 135) # 오른쪽 회피 기준
            motor.rear_backward(150, 135)
            time.sleep(0.5)
            
             # 전진 + 같은 조향
            motor.front_forward(150, 135)
            motor.rear_forward(150, 135)
            time.sleep(0.6)

            # 조향 초기화
            motor.front_forward(150, 90)
            motor.rear_forward(150, 90)
            
        else:
            print("[Action] 정적 장애물 감지 -> 감속")
            motor.front_forward(100, 90)
            motor.rear_forward(100, 90)
# 회피 알고리즘 요약 정지 
# → 후진 + 조향 → 전진 + 같은 조향 → 조향 초기화
