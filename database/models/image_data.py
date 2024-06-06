from sqlalchemy import Column, Integer, String
from database import Base

class ImageData(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    filename = Column(String, unique=True, index=True)