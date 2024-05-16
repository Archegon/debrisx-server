from flask import Flask, Response
import cv2
import time
import numpy as np
import requests
from object_detection.handler import predict_image

app = Flask(__name__)

# Replace with the IP address of your Raspberry Pi
RPI_IP = 'http://192.168.1.81:8000/stream.mjpg'

def fetch_mjpeg_stream():
    stream = requests.get(RPI_IP, stream=True)
    bytes = b''
    for chunk in stream.iter_content(chunk_size=1024):
        bytes += chunk
        a = bytes.find(b'\xff\xd8')
        b = bytes.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes[a:b+2]
            bytes = bytes[b+2:]
            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
                
start_time = time.time()
last_fps_time = start_time
frame_count = 0

def predicted_stream():
    global frame_count, start_time, last_fps_time

    stream = requests.get(RPI_IP, stream=True)
    bytes = b''
    for chunk in stream.iter_content(chunk_size=1024):
        bytes += chunk
        a = bytes.find(b'\xff\xd8')
        b = bytes.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes[a:b+2]
            bytes = bytes[b+2:]
            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            _, predicted_frame = predict_image(frame, postprocess=True, stream=True)
            ret, jpeg = cv2.imencode('.jpg', predicted_frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            
            # Update the frame count
            frame_count += 1

            # Get the current time
            current_time = time.time()

            # Calculate elapsed time since last FPS calculation
            elapsed_time = current_time - last_fps_time

            if elapsed_time >= 1.0:
                # Calculate FPS
                fps = frame_count / elapsed_time
                print(f"FPS: {fps:.2f}")

                # Reset the frame count and last_fps_time
                frame_count = 0
                last_fps_time = current_time


@app.route('/stream.mjpg')
def video_feed():
    return Response(fetch_mjpeg_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def video_predicted_feed():
    return Response(predicted_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
