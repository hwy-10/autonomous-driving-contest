# 좌/직/우에 대한 벡터값 -> 속도 및 방향 결정
from main_status import Status
from CNN import decide_highest_priority, decide_action, action_to_status


frame = afb.camera.get_image()  # 카메라로부터 프레임을 가져옴
cv_status = get_cv_status(frame)  # OpenCV로부터 상태를 결정

class_ids = detect_yolo_class_ids(frame) # YOLO로부터 클래스 ID를 감지
label = decide_highest_priority(class_ids)  # 가장 높은 우선순위 클래스 결정
action = decide_action(label)
cnn_status = action_to_status(action)  # CNN 상태로 변환


def get_cv_status(frame) -> Status:
    
    lane_center = get_lane_center(frame)
    
    if lane_center < 280:
        return Status.left
    
    elif lane_center > 360:
        return Status.right
    
    else:
        return Status.go
    
status, stop_count = decide_final_status(cv_status, cnn_status)  # 최종 상태 결정