from obstacles.base import *
from yolo_enum import YOLO_label

def label_to_obstacle(label: YOLO_label):
     match label:
        case YOLO_label.left | YOLO_label.sign_left:
            return TurnLeft()
        case YOLO_label.right | YOLO_label.sign_right:
            return TurnRight()
        case YOLO_label.hill_up:
            return Uphill(direction="up")
        case YOLO_label.hill_down:
            return Uphill(direction="down")
        case YOLO_label.sign_tunnel:
            return Tunnel()
        case YOLO_label.red_light:
            return TrafficLight("red")
        case YOLO_label.yellow_light:
            return TrafficLight("yellow")
        case YOLO_label.green_light:
            return TrafficLight("green")
        case YOLO_label.car:
            return StaticCar(distance=20)  # 예: 거리 추정값 들어감
        case YOLO_label.sign_stop:
            return DynamicObstacle()
        case _:
            return None
        
# 감지된 YOLO class ID 중 최우선 클래스 선택
def decide_highest_priority(detected_cls_ids):
    from yolo_enum import PRIORITY
    for label in PRIORITY:
        if label.value in detected_cls_ids:
            return label
    return None
