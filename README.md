# 자율주행경진대회

이미지 전처리 기법
1) Grayscale : 컬러 → 흑백 변환 목적 : 계산량 감소, 윤곽 강조
    OpenCV API 내장 코드값 이용!  “cv2.COLOR_BGR2GRAY”
    차선, 경계선, 정지선 인식에서는 색상보다 명암 대비가 더 중요하기 때문에 grayscale을 사용
2) Gaussian Blur
ggi
3) Binarization (Threshold)
    OpenCV 내장 함수 사용  “cv2.threshold()”
    
Canny Edge Detection	
Sobel/Scharr Filter	
Morphology (열림/닫힘)	
ROI 설정 (Region of Interest)	
Perspective Transform	
Histogram Equalization	
Color Masking (HSV)	
Adaptive Threshold	
Median Blur	
Image Resize

-- PID 제어 및 Canny edge -- 

@@ 차선 인식 @@ 
Motor 함수

----- 
autodrive_project/
├── main.py                         # 전체 실행 흐름
├── camera/                         # 카메라 관련
│   ├── __init__.py
│   └── camera_stream.py           # 카메라 스트리밍, 프레임 캡처
├── vision/                         # 시각 처리
│   ├── __init__.py
│   ├── yolov5_wrapper.py          # YOLO 로딩/검출
│   └── preprocess.py              # 이미지 전처리
├── control/                        # 차량 제어
│   ├── __init__.py
│   └── motor_control.py           # 속도, 조향 제어
├── obstacle_control/               # 주행 판단 로직
│   ├── __init__.py
│   └── decision.py                # 신호등, 장애물 판단
└── utils/
    ├── __init__.py
    └── logger.py                  # 로깅 및 디버깅


1 --함수 modulation을 사용해야 하는 이유
1-1 -- __init__.py의 역할
1-2 -- Modular Architecture
1-3 -- 자율주행 규정집에 따라 모듈을 어떻게 구성해볼까? 

2 -- SW 아키텍처란 무엇인가

3 -- 시각 처리(느림)와 모터 제어(빠름)을 어떻게 동시에 처리할까
3-1 -- 비동기식 async/await
3-2 -- threding