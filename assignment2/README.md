# Assignment 2
due Date : 2025.07.09 - 2025.07.15

Assignment 2_1 : traffic_light.mp4에 YOLOv8을 활용하여 신호등 인식 및 주행 판단(Stop/Go) 텍스트 표시(다른 모델을 사용하여도 무방)

YOLOv8 객체 탐지 모델을 사용해 비디오에 등장하는 신호등(빨간불, 초록불)을 실시간으로 검출하고, 각 신호에 따라 화면 상단에 'Stop'(빨간불) 또는 'Go'(초록불) 텍스트를 표시할 수 있다. 신호등의 Bounding Box, 클래스명, Confidence Score를 프레임에 함께 표시한다.

① OpenCV로 비디오(traffic light.mp4)를 로드합니다.
② 각 프레임에서 YOLOv8 모델로 신호등(빨간불/초록불)을 검출합니다.
③ 검출된 신호등에 대해 Bounding Box, 클래스명, Confidence Score를 표시합니다. (Red/Green)
④ 화면 상단에 빨간불일 때는 'Stop'을, 초록불일 때는 'Go' 텍스트를 시각화합니다.
⑤ 결과를 'Traffic Light Detection' 창에 실시간으로 출력합니다.
* 클래스 id는 데이터셋에 따라 다를 수 있으니 반드시 본인 모델에 맞는 id 사용

Assignment 2_2 : dog.mp4에 YOLOv8을 활용하여 장애물 인식 및 이동 경로에 따른 회피 방향(Avoid to the left / Avoid to the right) 텍스트 
표시(다른 모델을 사용하여도 무방)

YOLOv8 객체 탐지 모델을 사용해 비디오에 등장하는 dog를 검출하고, 최근 프레임의 이동 경로를 분석하여 이동 방향에 따른 회피 텍스트를 
2초간 표시할 수 있다. 검출된 bounding box와 클래스명도 프레임에 함께 시각화한다.

① OpenCV로 비디오(dog.mp4)를 로드합니다.
② 각 프레임에서 YOLOv8 모델로 dog 객체를 검출합니다.
③ 검출된 dog의 중심 좌표 변화를 기반으로 dog의 이동 방향을 계산
합니다.
④ dog가 이동 중일 경우, 'Avoid to the left' 또는 'Avoid to the right' 
텍스트를 2초 동안 화면 상단에 표시합니다.
⑤ 검출 결과를 'dog obstacle avoidance' 창에 실시간으로 출력합니다.

