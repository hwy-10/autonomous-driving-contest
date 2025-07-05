import urllib.request
import zipfile
import os
import datetime
import cv2
from ultralytics import YOLO
from glob import glob
from sklearn.model_selection import train_test_split
import yaml
import subprocess

# 1. 다운로드
url = "https://universe.roboflow.com/ds/mlmJAbJlDu?key=eWOXCXInoX"
output_path = "roboflow.zip"

urllib.request.urlretrieve(url, output_path)
print("✅ 다운로드 완료")

# 2. 압축 해제
with zipfile.ZipFile(output_path, 'r') as zip_ref:
    zip_ref.extractall("roboflow_dataset")
print("✅ 압축 해제 완료")

# 3. 원본 zip 삭제
os.remove(output_path)
print("✅ ZIP 삭제 완료")

#라벨링된 데이터를 roboflow에서 다운로드받고 unzip을 하는 과정
#!curl -L "https://app.roboflow.com/ds/QWCdLWmuAn?key=0DhraHMsrY" > roboflow.zip; unzip roboflow.zip; rm roboflow.zip


#우리가 다운로드한 이미지의 길이 즉 몇장인지 확인
img_list = glob('roboflow_dataset\\train\\images\\*.jpg')

print(len(img_list))

#우리가 다운로드받은 데이터셋 -> 모두 train파일에 들어가있음. 즉 test데이터셋과 train데이터셋이 나누어지지 않음
#따라서 0.3 즉 30%를 테스트 데이터셋으로 만드는 과정
train_img_list, val_img_list = train_test_split(img_list, test_size=0.3, random_state=2000)
train_img_list = [os.path.abspath(path) for path in train_img_list]
val_img_list = [os.path.abspath(path) for path in val_img_list]
print(len(train_img_list), len(val_img_list))

#txt파일을 생성하여 이미지의 경로를 모두 지정함.
with open('train.txt', 'w') as f:
  f.write('\n'.join(train_img_list) + '\n')

with open('val.txt', 'w') as f:
  f.write('\n'.join(val_img_list) + '\n')



yaml_path = 'roboflow_dataset/data.yaml'  # 슬래시로 경로 수정

# 파일 존재 여부 확인
if os.path.exists(yaml_path):
    print(f"✅ 파일 존재함: {yaml_path}")
else:
    print(f"❌ 파일 없음: {yaml_path}")


yaml_path = 'roboflow_dataset/data.yaml'

# 1. 기존 YAML 불러오기
with open(yaml_path, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

print("🔍 기존 내용:", data)

# 2. 수정
data['train'] = os.path.abspath("train.txt")
data['val'] = os.path.abspath("val.txt")

# 3. 다시 저장 (중요: sort_keys, flush)
with open(yaml_path, 'w', encoding='utf-8') as f:
    yaml.dump(data, f, sort_keys=False)
    f.flush()
0
print("✅ 수정된 내용:", data)

# Load a model
model = YOLO("yolov8n.pt")  # build a new model from scratch

drive_dir = "roboflow"

# Use the model
results = model.train(data="roboflow_dataset/data.yaml", epochs = 5, project=drive_dir, name='yolov8n_training')