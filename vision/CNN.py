import cv2
from ultralytics import YOLO
from enum import Enum
from runtime.config import *
from runtime import camera

model = YOLO("best.pt") # 이 YOLO 모델을 학습 시킬 예정 main에서 vision을 import 시 자동으로 모델이 로드되게 설정


def _detect_class_id(frame):
    try:
        if frame is None:
            print("❌ 프레임을 가져오지 못했습니다.")
            return []

        result = model(frame)[0]
        detected_cls_ids = []
        area = None 
        for box in result.boxes:
            cls_id = int(box.cls[0])
            detected_cls_ids.append(cls_id)

            conf = float(box.conf[0])
            label = model.names[cls_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if label == "car":
                area = (x2-x1)*(y2-y1)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        return detected_cls_ids, area

    except Exception as e:
        print("❌ YOLO 예측 오류:", e)
        return []


def _decide_highest_priority(frame): # Enum 객체를 반환
    detected_cls_ids, area = _detect_class_id(frame)

    for label in PRIORITY:
        if label.value in detected_cls_ids:
            return label, area
    return None, area

def get_cnn_status(frame) -> Status:
    
    label, area = _decide_highest_priority(frame)

    if label == "car" and area >= 150:
        return Status.avoid

    mapping = {
    YOLO_label.sign_stop: Status.stop,
    YOLO_label.red_light: Status.stop,
    YOLO_label.car: Status.go, # 아직 차량과 가깝지 않다면, 회피 기능을 실행하지 않고 직진을 수행 

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

def decide_final_status(cnn_status): # Status class, stop_count 반환
    # 1. stop 누적 판단 따로 처리
    if cnn_status == Status.stop:
        stop_count += 1
        if stop_count >= stop_threshold:
            return Status.stop, stop_count
        else:
            return Status.decelerate, stop_count # 일단 stop 시그널을 보냈을 때, 감속하는 방식으로

    stop_count = 0

    return cnn_status, stop_count