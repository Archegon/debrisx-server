from flask import Flask, Response
from flask_socketio import SocketIO, Namespace
import cv2
import time
import base64
import numpy as np
from queue import Queue
from object_detection.handler import predict_image

app = Flask(__name__)
socketio = SocketIO(app)
frame_queue = Queue(maxsize=10)  # holds up to 10 frames to avoid memory issues

def generate_frames():
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            _, buffer = cv2.imencode('.jpg', frame)  # Encode frame as JPEG
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        else:
            time.sleep(0.1)  # Wait if no frames are available

class DebrisxNamespace(Namespace):
    def on_connect(self):
        print("Client connected")

    def on_disconnect(self):
        print("Client disconnected")

    def on_send_frame(self, data):
        frame_data = base64.b64decode(data['frame'])  # Decode the base64 string
        frame_array = np.frombuffer(frame_data, dtype=np.uint8)
        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)  # Decode the image data to an OpenCV format

        if frame is not None:
            processed_frame = predict_image(frame)  # Process the image
            if not frame_queue.full():
                frame_queue.put(processed_frame)  # Store the processed frame in the queue
        else:
            print("Failed to decode frame")

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    # Return a simple webpage with the video stream embedded
    return Response('<html><body><img src="/video_feed"></body></html>')

# Register the namespace
socketio.on_namespace(DebrisxNamespace('/debrisx'))