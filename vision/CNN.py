from enum import Enum

"""
YOLO 모델이 예측한 YOLO_label을 뱉어줌
e.g> detected_cls_ids = [1, 9, 10]
"""



class YOLO_label(Enum): # 크게 보면 go, back, stop 
    left = 0
    straight = 1
    right = 2
    hill_up = 3
    hill_down = 4
    sign_left = 5
    sign_right = 6
    sign_tunnel= 7
    sign_stop = 8 # 차단기
    red_light = 9
    yellow_light = 10
    green_light = 11
    car = 12
# 차량 운행 알고리즘에 따라 label 변경 가능


# 우선순위를 list로 관리
PRIORITY = [
    YOLO_label.sign_stop,
    YOLO_label.red_light,
    YOLO_label.car,

    YOLO_label.yellow_light,
    YOLO_label.green_light,

    YOLO_label.sign_tunnel,
    YOLO_label.sign_left,
    YOLO_label.sign_right,

    YOLO_label.hill_up,
    YOLO_label.hill_down,

    YOLO_label.left,
    YOLO_label.straight,
    YOLO_label.right   
]

# 탐지된 class id 중에서 가장 우선순위가 높은 Enum 객체를 반환하는 함수
def decide_highest_priority(detected_cls_ids): # Enum 객체를 반환
    """
    감지된 클래스 ID들 중에서 PRIORITY 리스트에서 가장 우선순위가 높은 것을 선택.
    """
    for label in PRIORITY:
        if label.value in detected_cls_ids:
            return label  # 가장 높은 우선순위 클래스 반환
    return None  # 해당 없음

# decide_hightest_priority를 통해 결정된 label을 넣어서 취해야할 action을 결정
def decide_action(label: YOLO_label) -> str:
    mapping = {
    YOLO_label.sign_stop: "stop",
    YOLO_label.red_light: "stop",
    YOLO_label.car: "avoid",

    YOLO_label.yellow_light: "decelerate",
    YOLO_label.green_light: "go",

    YOLO_label.sign_tunnel: "go", # 터널 표지판 시 action을 무엇을 할 지 의문
    YOLO_label.sign_left: "left",
    YOLO_label.sign_right: "go",

    YOLO_label.hill_up: "accelerate",
    YOLO_label.hill_down: "decelerate",

    YOLO_label.left: "left",
    YOLO_label.straight: "go",
    YOLO_label.right: "right"

# all action: go, left, right, stop, avoid, accel, decel 총 7개 상태

    }
    return mapping.get(label, "go")

"""
class: YOLO
1) 좌회전 
2) 직진 
3) 우회전
4) 언덕(가속)
5) 언덕(감속)
6) 표지판 : 우회전
7) 표지판 : 좌회전
8) 표지판 : 터널 
9) 동적장애물 : 정지
10) 신호등: 빨
11) 신호등: 주
12) 신호등: 초 
13) 정적장애물(차)
"""

