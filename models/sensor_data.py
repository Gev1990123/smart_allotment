from datetime import datetime
from . import db

class SensorReading(db.Model):
    __tablename__ = 'sensor_readings'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sensor_type = db.Column(db.String(50))  # e.g., 'soil_moisture', 'temperature'
    value = db.Column(db.Float)
    device_id = db.Column(db.String(50), nullable=True)  # optional for multiple Pi Zeros

    def __repr__(self):
        return f"<SensorReading {self.sensor_type}={self.value} at {self.timestamp}>"
