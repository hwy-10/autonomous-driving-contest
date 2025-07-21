from ultralytics import YOLO
from enum import Enum
from . import camera
import cv2
from config import Status
"""
YOLO 모델이 예측한 YOLO_label을 뱉어줌
e.g> detected_cls_ids = [1, 9, 10]
"""

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

def _get_image(): # resize된 사진을 return 해주는 내부 함수
    frame = camera.get_image
    frame = cv2.resize(frame, (640, 480))
    return frame

def _detect_class_id():
    try:
        frame = _get_image()
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

# 탐지된 class id 중에서 가장 우선순위가 높은 Enum 객체를 반환하는 함수
def _decide_highest_priority(): # Enum 객체를 반환
    """
    감지된 클래스 ID들 중에서 PRIORITY 리스트에서 가장 우선순위가 높은 것을 선택.
    """
    detected_cls_ids = _detect_class_id()

    for label in PRIORITY:
        if label.value in detected_cls_ids:
            return label  # 가장 높은 우선순위 클래스 반환
    return None  # 해당 없음

# decide_hightest_priority를 통해 결정된 label을 넣어서 취해야할 action을 결정
def get_cnn_status() -> Status:
    label = _decide_highest_priority()

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
    return mapping.get(label, Status.go) # mapping이 없을 때는 기본적으로 go를 반환