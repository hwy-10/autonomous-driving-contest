from enum import Enum

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

# back은 openCV로만 구현 -> 이후 CNN으로도 구현해야 한다면, 구현하기
# CNN: go, left, right, stop, avoid, accel, decel 총 7개 상태