from sqlalchemy import Column, Integer, Float, DateTime
from database import Base

class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    ph = Column(Float, nullable=False)
    tds = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)