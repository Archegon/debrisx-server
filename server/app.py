import cv2
import time
import base64
import numpy as np
from flask import Flask, Response
from flask_socketio import SocketIO, Namespace
from threading import Thread
from queue import Queue, Full
from object_detection.handler import predict_image

app = Flask(__name__)
socketio = SocketIO(app)

frame_queue = Queue(maxsize=1)
processed_frame_queue = Queue(maxsize=1)  # holds up to 10 frames to avoid memory issues

fps = 0
frame_count = 0
start_time = time.time()
current_frame = None

def generate_frames():
    global fps
    while True:
        if not processed_frame_queue.empty():
            frame = processed_frame_queue.get()

            # Apply the FPS text to the frame
            cv2.putText(frame, f'FPS: {fps}', (475, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            _, buffer = cv2.imencode('.jpg', frame)  # Encode frame as JPEG

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        else:
            time.sleep(0.0167)  # Wait if no frames are available

def frame_processor():
    global frame_count, fps, start_time
    while True:
        if not frame_queue.empty():
            frame_data = frame_queue.get()
            frame_count += 1

            try:
                # Decode the image from base64 and convert to OpenCV format
                img_data = base64.b64decode(frame_data)
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if img is not None:
                    # Perform inference
                    results = predict_image(img)
                else:
                    print("Failed to decode frame")
                
                # Store the processed frame in the queue
                if not processed_frame_queue.full():
                    processed_frame_queue.put(results)  

            except Exception as e:
                print(f"Failed to process frame: {e}")

            # Calculate FPS every second
            current_time = time.time()
            if current_time - start_time >= 1:
                fps = round(frame_count / (current_time - start_time))
                frame_count = 0
                start_time = current_time

w_start_time = time.time()
receive_count = 0

class DebrisxNamespace(Namespace):
    def on_connect(self):
        print("Client connected")

    def on_disconnect(self):
        print("Client disconnected")

    def on_send_frame(self, data):
        global receive_count, w_start_time

        receive_count += 1

        if time.time() - w_start_time >= 1:
            print(f"Receiving Rate: {receive_count} per s")
            w_start_time = time.time()
            receive_count = 0
            
        try:
            frame_queue.put(data['frame'], timeout=1)
        except Full:
            pass

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

# Start the processing thread
thread = Thread(target=frame_processor)
thread.daemon = True
thread.start()