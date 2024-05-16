import cv2
import time
import base64
import numpy as np
from flask import Flask, Response
from flask_socketio import SocketIO, Namespace, emit
from threading import Thread
from object_detection.handler import predict_image

app = Flask(__name__)
socketio = SocketIO(app)

unprocessed_frame = None
processed_frame = None

fps = 0
frame_count = 0
start_time = time.time()

def generate_frames():
    global fps, processed_frame

    while True:
        if processed_frame is not None:
            data = processed_frame
            processed_frame = None
            frame = data["image"]

            # Apply the FPS text to the frame
            cv2.putText(frame, f'FPS: {fps}', (475, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            _, buffer = cv2.imencode('.jpg', frame)  # Encode frame as JPEG

            print(f"Total Processing latency: {(time.time() - data['time_received']) * 1000:.2f} ms")

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

def frame_processor(raw=False):
    global frame_count, fps, start_time, unprocessed_frame, processed_frame

    while True:
        if unprocessed_frame is not None:
            frame_data = unprocessed_frame
            unprocessed_frame = None
            time_received = time.time()
            frame_count += 1

            try:
                # Decode the image from base64 and convert to OpenCV format
                img_data = base64.b64decode(frame_data)
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if raw:
                    if processed_frame is None:
                        processed_frame = {"image": img, "time_received": time_received}
                else:
                    if img is not None:
                        # Perform inference
                        results = predict_image(img)
                    else:
                        print("Failed to decode frame")
                    
                    if processed_frame is None:
                            processed_frame = {"image": results, "time_received": time_received}

            except Exception as e:
                print(f"Failed to process frame: {e}")

            # Calculate FPS every second
            current_time = time.time()
            if current_time - start_time >= 1:
                fps = round(frame_count / (current_time - start_time))
                frame_count = 0
                start_time = current_time

class DebrisxNamespace(Namespace):
    def on_connect(self):
        print("Client connected")

    def on_disconnect(self):
        print("Client disconnected")

    def on_start_latency_test(self, data):
        self.emit_latency_test()

    def on_send_frame(self, data):
        global unprocessed_frame

        payload = {
            "client_sendtime" : data['client_sendtime'],
        }

        emit('frame_latency', payload, namespace='/debrisx')

        if unprocessed_frame is None:
            unprocessed_frame = data['frame']

    def emit_latency_test(self):
        # Send current time to the client and request immediate response
        start_time = time.time()
        emit('test_latency', {'server_time': start_time}, namespace='/debrisx')

    def on_latency_response(self, data):
        # Receive the latency response from the client with its timestamp
        end_time = time.time()
        server_time = data['server_time']

        # Calculate the round trip latency
        rtt = (end_time - server_time) * 1000

        print(f"Round-trip time: {rtt:.2f} ms")

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
thread = Thread(target=frame_processor, kwargs={'raw': True})
thread.daemon = True
thread.start()