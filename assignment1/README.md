# Assignment 1
Due Date : 2025.07.02 - 2025.07.08

Assignment 1_1 : 3일차 강의 lec\L_5_capture 코드를 이용한 차선 촬영 후 차선 인식 진행

내용 : 실제 주행 트랙에서 차선을 검출하고, 차량의 진행 방향(Direction)을 실시간으로 계산하고 표시
3일차 강의에서 제공한 L_5 코드로 직접 트랙을 촬영하여 차선 표시해보기

⓵ 각자 4일차 실습 시간 때 트랙의 사진을 찍는다. 
⓶ 다양한 차선 인식 기법을 활용하여 프레임별 차선을 검출합니다.
⓷ 후에 좌/우/직진을 판단하기 위해 팀별로 원하는 방식을 선택하여 검출된 결과를 제출

Assignment 1_2 : Video에서 차량 검출 및 Bouding Box 시각화

내용 : roadcam.mp4에 YOLOv8(혹은 다른 버전)을 활용하여 차량 인식 및 Bounding Box 표시
YOLOv8 객체 탐지 모델을 사용해 비디오에 등장하는 차량을 실시간으로 검출하여 Bounding Box, 클래스명, Confidence Score를 프레임에 
표시할 수 있다. (yolo는 다른 모델을 사용하여도 무방.)

⓵ OpenCV로 비디오('roadcam.mp4’)를 로드합니다. 
⓶ 각 프레임에서 YOLOv8 모델로 객체(car, motocycle, bus)를 검출합니다.
⓷ 검출된 객체에 대해 Bounding Box, 클래스명, Confidence Score를 표시합니다.
⓸ 검출된 결과를 ‘Vehicle Detection’ 창에 실시간으로 출력합니다.
