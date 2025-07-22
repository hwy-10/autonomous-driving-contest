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

PRIORITY= [
        Status.stop,
        Status.avoid,
        # Status.back, # back은 실제로 구현 x 
        Status.accelerate,
        Status.decelerate,
        Status.go,
        Status.left,
        Status.right
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

    return cnn_status, stop_count