import os
import cv2
import time
import asyncio
import aiohttp
import numpy as np
from object_detection.handler import predict_image

class StreamPredictor:
    def __init__(self, rpi_ip):
        self.rpi_ip = rpi_ip
        self.start_time = time.time()
        self.last_fps_time = self.start_time
        self.frame_count = 0
        self.stop_stream = False
        self.streaming_task = None
        self.processing_task = None
        self.frame_queue = asyncio.Queue()
        self.predicted_frame_queue = asyncio.Queue()

    def start_streaming(self):
        if self.streaming_task is None or self.streaming_task.done():
            self.stop_stream = False
            self.streaming_task = asyncio.create_task(self.run_read_stream())
            self.processing_task = asyncio.create_task(self.process_frames())

    def stop_streaming(self):
        self.stop_stream = True
        if self.streaming_task:
            self.streaming_task.cancel()
        if self.processing_task:
            self.processing_task.cancel()

    async def run_read_stream(self):
        async for _ in self.read_stream():
            if self.stop_stream:
                break

    async def read_stream(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.rpi_ip + "/stream.mjpg") as response:
                    if response.status != 200:
                        print(f"Error: {response.status}")
                        return
                    bytes = b''
                    async for chunk in response.content.iter_chunked(1024):
                        if self.stop_stream:
                            break
                        bytes += chunk
                        a = bytes.find(b'\xff\xd8')
                        b = bytes.find(b'\xff\xd9')
                        if a != -1 and b != -1:
                            jpg = bytes[a:b+2]
                            bytes = bytes[b+2:]
                            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                            if frame is not None:
                                await self.frame_queue.put(frame)
                            yield frame
        except aiohttp.ClientError as e:
            print(f"Error: {e}")

    def predict_and_encode(self, frame):
        _, predicted_frame = predict_image(frame, postprocess=True, stream=True)
        ret, jpeg = cv2.imencode('.jpg', predicted_frame)
        if ret:
            return jpeg.tobytes()
        
    async def process_frames(self):
        while not self.stop_stream:
            frame = await self.frame_queue.get()
            jpeg = await asyncio.to_thread(self.predict_and_encode, frame)
            if jpeg:
                await self.predicted_frame_queue.put(jpeg)
                self.calculate_fps()

    def calculate_fps(self):
        self.frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self.last_fps_time
        if elapsed_time >= 1.0:
            fps = self.frame_count / elapsed_time
            print(f"FPS: {fps:.2f}")
            self.frame_count = 0
            self.last_fps_time = current_time

    async def predicted_stream(self):
        while not self.stop_stream:
            jpeg = await self.predicted_frame_queue.get()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')

RPI_IP = os.getenv('RPI_IP')

if not RPI_IP:
    raise EnvironmentError("RPI_IP environment variable not set")

stream_predictor = StreamPredictor(RPI_IP)