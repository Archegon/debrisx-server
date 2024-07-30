import os
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api import api_router
from .websockets.connection import websocket_endpoint
from database import Base, engine

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await websocket_endpoint(websocket)

# Print the absolute path for debugging
uploads_dir = os.path.abspath("./uploads")
app.mount("/static", StaticFiles(directory=uploads_dir), name="static")