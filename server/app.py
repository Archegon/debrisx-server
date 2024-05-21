from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import api_router
from database import Base, engine

app = FastAPI()

# Create database tables
# Base.metadata.create_all(bind=engine)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
