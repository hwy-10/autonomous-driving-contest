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
        return "좌회전 실행"

class TurnRight(Obstacle):
    def __init__(self):
        super().__init__("우회전", priority=1)

    def action(self):
        return "우회전 실행"

class Uphill(Obstacle):
    def __init__(self, direction="up"):
        super().__init__("언덕", priority=2)
        self.direction = direction

    def action(self):
        return "가속" if self.direction == "up" else "감속"

class Tunnel(Obstacle):
    def __init__(self):
        super().__init__("터널", priority=1)

    def action(self):
        return "전조등 켜기 + 속도 유지"

class DynamicObstacle(Obstacle):
    def __init__(self, label, priority=3):
        super().__init__("동적장애물", priority = 5)
        self.direction = direction # 향후 좌, 우 확장
        
    def action(self):
        return "동적 장애물 감지 -> 정지"

class TrafficLight(Obstacle):
    def __init__(self, color):
        super().__init__("신호등", priority=4)
        self.color = color  # "red", "green", "yellow"

    def action(self):
        if self.color == "red":
            return "빨간불 감지 → 정지"
        elif self.color == "green":
            return "초록불 감지 → 직진"
        elif self.color == "yellow":
            return "노란불 감지 → 감속"
        else:
            return "알 수 없는 신호등 색상"
        
class StaticCar(Obstacle):
    def __init__(self, distance=None):
        super().__init__("정적장애물", priority=3)
        self.distance = distance # 거리 정보 활용 가능 (거리 센서 값 (cm))

    def action(self):
        if self.distance is not None and self.distance < 30:
            return "정적 장애물 감지 → 정지 또는 회피"
        else:
            return "정적 장애물 감지 → 감속 또는 주시"
