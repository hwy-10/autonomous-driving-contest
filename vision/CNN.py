import cv2
from ultralytics import YOLO
from enum import Enum
from runtime.config import Status
from runtime import camera

"""
YOLO 모델이 예측한 YOLO_label을 뱉어줌
e.g> detected_cls_ids = [1, 9, 10]
"""

# model = YOLO("yolov8n.pt")  # YOLO 모델 로드

'''
def detect_yolo_class_ids(frame):
    results = model(frame)[0]  # YOLO 모델로부터 결과 추출
    return [int(cls_id) for cls_id in results.boxes.cls.tolist()]
'''

model = YOLO("best.pt") # 이 YOLO 모델을 학습 시킬 예정


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
    car = 12 # 정적 장애물 
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

def _detect_class_id(frame):
    try:
        if frame is None:
            print("❌ 프레임을 가져오지 못했습니다.")
            return []

        result = model(frame)[0]
        detected_cls_ids = []

        for box in result.boxes:
            cls_id = int(box.cls[0])
            detected_cls_ids.append(cls_id)

            conf = float(box.conf[0])
            label = model.names[cls_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        return detected_cls_ids

    except Exception as e:
        print("❌ YOLO 예측 오류:", e)
        return []


def _decide_highest_priority(frame): # Enum 객체를 반환
    """
    감지된 클래스 ID들 중에서 PRIORITY 리스트에서 가장 우선순위가 높은 것을 선택.
    """
    detected_cls_ids = _detect_class_id(frame)

    for label in PRIORITY:
        if label.value in detected_cls_ids:
            return label
    return None

# decide_hightest_priority를 통해 결정된 label을 넣어서 취해야할 action을 결정
# YoLo_label -> 행동 문자열 mapping

# def decide_action(label: YOLO_label) -> str:

def get_cnn_status(frame) -> Status:
    
    label = _decide_highest_priority(frame)

    mapping = {
    YOLO_label.sign_stop: Status.stop,
    YOLO_label.red_light: Status.stop,
    YOLO_label.car: Status.avoid,

    YOLO_label.yellow_light: Status.decelerate,
    YOLO_label.green_light: Status.go,

    YOLO_label.sign_tunnel: Status.go, # 터널 표지판 시 action을 무엇을 할 지 의문
    YOLO_label.sign_left: Status.left,
    YOLO_label.sign_right: Status.right,

    YOLO_label.hill_up: Status.accelerate,
    YOLO_label.hill_down: Status.decelerate,

    YOLO_label.left: Status.left,
    YOLO_label.straight: Status.go,
    YOLO_label.right: Status.right
    }
    return mapping.get(label, "go")


def action_to_status(action: str) -> Status:
     mapping = {
        "go": Status.go,
        "left": Status.left,
        "right": Status.right,
        "stop": Status.stop,
        "avoid": Status.avoid,
        "accelerate": Status.accelerate,
        "decelerate": Status.decelerate
    }
    return mapping.get(action, Status.go)

'''
# 최종 CNN 기반 status 추출 함수
def get_cnn_status(frame) -> Status:
    detected_cls_ids = detect_yolo_class_ids(frame)  # YOLO로부터 감지된 클래스 ID 리스트
    label = decide_highest_priority(detected_cls_ids)  # 가장 우선순위가 높은 label 선택
    if label is None:
        return Status.go
    
    action = decide_action(label)  # 해당 label에 따른 행동 결정
    return action_to_status(action)
'''

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