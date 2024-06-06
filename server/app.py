import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .api import api_router
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

# Print the absolute path for debugging
uploads_dir = os.path.abspath("./uploads")
print(f"Static files directory: {uploads_dir}")

app.mount("/static", StaticFiles(directory="./uploads"), name="static")
