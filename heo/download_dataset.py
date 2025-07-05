import os
from roboflow import Roboflow


# Roboflow에서 데이터 다운로드
rf = Roboflow(api_key="ullF14Ho1gM87iJHYDnQ")
project = rf.workspace("hwy10").project("car_tt-nzo4f")
version = project.version(2)
dataset = version.download("yolov8")

# 다운로드된 폴더 경로 출력
print("📁 다운로드 위치:", dataset.location)

