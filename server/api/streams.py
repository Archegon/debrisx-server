from fastapi.responses import StreamingResponse
from server.modules.streams import stream_predictor
from .router import api_router

@api_router.get("/raw_feed", tags=["Video Operations"])
async def video_raw_feed():
    """
    Returns the raw video feed as a streaming response.
    """
    return StreamingResponse(stream_predictor.raw_stream(), media_type='multipart/x-mixed-replace; boundary=frame')

@api_router.get("/raw_feed/start", tags=["Video Operations"])
async def start_video_raw_feed():
    """
    Starts the video feed prediction.
    """
    stream_predictor.start_streaming(raw_stream=True)
    return {"message": "Streaming started"}

@api_router.get("/predicted_feed", tags=["Video Operations"])
async def video_predicted_feed():
    """
    Returns the predicted video feed as a streaming response.
    """
    return StreamingResponse(stream_predictor.predicted_stream(), media_type='multipart/x-mixed-replace; boundary=frame')

@api_router.get("/predicted_feed/start", tags=["Video Operations"])
async def start_video_predicted_feed():
    """
    Starts the video feed prediction.
    """
    stream_predictor.start_streaming(raw_stream=False)
    return {"message": "Streaming started"}

@api_router.get("/predicted_feed/stop", tags=["Video Operations"])
async def stop_video_predicted_feed():
    """
    Stops the video feed prediction.
    """
    stream_predictor.stop_streaming()
    return {"message": "Streaming stopped"}

@api_router.get("/predicted_feed/status", tags=["Video Operations"])
async def get_video_predicted_feed_status():
    """
    Returns the status of the video feed prediction.
    """
    return {
        "status": {
            "streaming": not stream_predictor.stop_stream,
            "processing": stream_predictor.processing_task is not None
            },
        "fps": stream_predictor.current_fps,
        }