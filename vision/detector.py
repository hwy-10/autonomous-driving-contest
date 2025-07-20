from obstacles.base import *

def detect_obstacle_from_frame(frame):
    """
    frame을 분석하여 장애물 클래스를 반환한다.
    예시를 위해 난수/조건으로 결정
    """
    detected_label = "right_sign"  # 예시: YOLO에서 나온 label 이름

    if detected_label == "right_sign":
        return TurnRight()
    elif detected_label == "tunnel":
        return Tunnel()
    elif detected_label == "static_car":
        return Obstacles("정적장애물", priority=3)
    
    elif detected_label == "dynamic_obstacle":
        return DynamicObstacle("동적장애물", priority=5)

    elif detected_label == "traffic_light":
        return TrafficLight("red")  # 예시: 빨간불

    elif detected_label == "static_car":
        return StaticCar(distance=25) 
    
    # elif detected_labe == "":
    #    return 

    else:
        return None  # 감지 안됨
