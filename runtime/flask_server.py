# Flask 서버 사용을 위함

from flask import Flask, render_template, Response
import cv2
from runtime import camera  # Pi Camera
from runtime.config import Status

app = Flask(__name__)

# 서버 상태 저장용 전역 변수
current_frame = None
current_status = Status.go
current_angle = 90

def generate_video():
    global current_frame
    while True:
        frame = camera.get_image()
        current_frame = frame
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

@app.route('/')
def index():
    return "🚗 자율주행 Flask 서버 작동 중!"

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    return {
        'status': str(current_status.name),
        'angle': current_angle
    }

# 외부에서 상태 업데이트 가능하게
def update_state(status, angle):
    global current_status, current_angle
    current_status = status
    current_angle = angle

def start_server():
    camera.init(640, 480, 30)
    app.run(host='0.0.0.0', port=5000, debug=False)
