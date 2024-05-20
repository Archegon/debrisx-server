from pydantic import BaseModel
from datetime import datetime

class SensorDataBase(BaseModel):
    ph: float
    temperature: float
    tds: float

class SensorDataCreate(SensorDataBase):
    timestamp: datetime

class SensorData(SensorDataBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True