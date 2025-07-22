from vision import camera
from vision import CNN
from vision import Lanepilot
import motor_control
import time

def avoid() :
               # 1) 감속(decelerate 속도) 유지
                speed = 150
 
                # 2) 장애물 위치 파악 (CNN)
                frame = camera.get_image()
                detections = CNN.detect_objects(frame)
                obstacle = next((bbox for lbl, bbox in detections if lbl == CNN.YOLO_label.car), None)
                obj_cx = Lanepilot.CENTER_X if obstacle is None else obstacle[0] + obstacle[2] // 2 

                # 3) 장애물 반대 방향으로 회피 각도 계산
                if obj_cx < Lanepilot.CENTER_X:
                    avoid_angle = 135  # 장애물이 왼쪽 → 우회전
                else:
                    avoid_angle = 45   # 장애물이 오른쪽 → 좌회전

                # 4) 원래 위치(직진 90°)에서 벗어난 만큼 보정 각도 계산
                #    offset = avoid_angle - 90, recover_angle = 90 - offset
                offset = avoid_angle - 90
                recover_angle = 90 - offset

                # 5) 1차 회피: 감속 + 조향
                motor_control.front_forward(speed, avoid_angle)
                motor_control.rear_forward(speed, avoid_angle)
                time.sleep(0.5)

                # 6) 2차 복귀: 감속 + 역조향
                motor_control.front_forward(speed, recover_angle)
                motor_control.rear_forward(speed, recover_angle)
                time.sleep(0.5)
                #------------------------------------------------------------