import afb
import time
import cv2 

afb.camera.init(640, 480, 30)

while True:
    frame = afb.camera.get_image()
    
    # BGR → RGB 변환
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # RGB로 웹 전송
    afb.flask.imshow("AFB Camera", frame_rgb, 0)
    afb.flask.imshow("SLOT1", frame_gray, 1)
    afb.flask.imshow("SLOT2", frame_rgb, 2)
    afb.flask.imshow("SLOT3", frame_gray, 3)