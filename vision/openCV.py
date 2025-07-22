# 좌/직/우에 대한 벡터값 -> 속도 및 방향 결정
from runtime.config import Status
from CNN import _decide_highest_priority, decide_action, action_to_status


def get_cnn_status(frame):
    try:
        detected_cls_ids = detect_yolo_class_ids(frame)
        if not detected_cls_ids:
            return Status.go  # default behavior

        label = decide_highest_priority(detected_cls_ids)
        if label is None:
            return Status.go

        action = decide_action(label)
        cnn_status = action_to_status(action)

        return cnn_status

    except Exception as e:
        print(f"[ERROR] CNN Status 처리 중 오류 발생: {e}")
        return Status.go