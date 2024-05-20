from sqlalchemy.orm import Session
from database.models import sensor_data as models
from database.schemas import sensor_data as schemas

def get_sensor_data(db: Session, data_id: int):
    return db.query(models.SensorData).filter(models.SensorData.id == data_id).first()

def create_sensor_data(db: Session, sensor_data: schemas.SensorDataCreate):
    db_sensor_data = models.SensorData(
        ph=sensor_data.ph,
        tds=sensor_data.tds,
        timestamp=sensor_data.timestamp
    )
    db.add(db_sensor_data)
    db.commit()
    db.refresh(db_sensor_data)
    return db_sensor_data