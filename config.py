from enum import Enum

stop_count = 0
stop_threshold = 3

class Status(Enum) :
    go = 0
    left = 1
    right = 2
    back = 3
    stop = 4
    avoid = 5
    accelerate = 6
    decelerate = 7

PRIORITY_RULES = [
        ("cnn", Status.stop),
        ("cnn", Status.avoid),
        ("cnn", Status.back)
        ("cnn", Status.accelerate),
        ("cnn", Status.decelerate),
        ("both", Status.go),
        ("both", Status.left),
        ("both", Status.right)
    ]

def decide_final_status(cv_status, cnn_status): # Status class, stop_count 반환
    # 1. stop 누적 판단 따로 처리
    if cnn_status == Status.stop:
        stop_count += 1
        if stop_count >= stop_threshold:
            return Status.stop, stop_count
        else:
            return Status.decelerate, stop_count # 일단 stop 시그널을 보냈을 때, 감속하는 방식으로

    stop_count = 0

    # 2. 우선순위 순회
    for source, rule_status in PRIORITY_RULES:
        if source == "cnn" and cnn_status == rule_status:
            return rule_status, stop_count
        if source == "both" and cnn_status == rule_status and cv_status == rule_status: # both일 때, 가중치를 두기
            return rule_status, stop_count
            # 굳이 같을 때 하지 않고, ex) cv = go cnn = right 라면 steering angle만 변화를 주면 될듯
    return Status.go, stop_count # 일단 두 상태가 다른 경우에는 go라고 코드가 작성되어 있음. 추후 변경