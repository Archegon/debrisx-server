import pytest
from unittest.mock import patch, MagicMock
import numpy as np
from server.modules.streams import StreamPredictor

@pytest.fixture
def mock_requests_get(monkeypatch):
    mock_stream = MagicMock()
    mock_stream.iter_content = MagicMock(return_value=[b'\xff\xd8', b'fake_image_data', b'\xff\xd9'])
    monkeypatch.setattr('server.modules.streams.requests.get', lambda url: mock_stream)

@pytest.fixture
def mock_imdecode(monkeypatch):
    mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    monkeypatch.setattr('server.modules.streams.cv2.imdecode', lambda buffer, flags: mock_frame)
    return mock_frame

@pytest.fixture
def mock_predict_image(monkeypatch):
    mock_predicted_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    monkeypatch.setattr('server.modules.streams.predict_image', lambda image: (None, mock_predicted_frame))
    return mock_predicted_frame

@pytest.fixture
def mock_imencode(monkeypatch):
    monkeypatch.setattr('server.modules.streams.cv2.imencode', lambda ext, img: (True, np.array([1, 2, 3])))

def test_read_stream(mock_requests_get, mock_imdecode, mock_predict_image, mock_imencode):
    # Initialize StreamPredictor
    predictor = StreamPredictor("http://fake_ip")

    # Read stream and get frames
    frames = list(predictor.read_stream())

    # Assert that frames are read correctly
    assert len(frames) == 1
    assert (frames[0] == mock_imdecode).all()

@pytest.mark.asyncio
async def test_predicted_stream(mock_requests_get, mock_imdecode, mock_predict_image, mock_imencode):
    # Initialize StreamPredictor
    predictor = StreamPredictor("http://fake_ip")

    # Test predicted_stream method
    async for frame in predictor.predicted_stream():
        assert frame.startswith(b'--frame\r\n')