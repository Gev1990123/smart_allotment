from datetime import datetime
from . import db

class Alert(db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    alert_type = db.Column(db.String(50))
    sensor_name = db.Column(db.String(50))
    value = db.Column(db.Float)
    last_notified = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active')

    def __repr__(self):
        return f"<Alert {self.alert_type} {self.sensor_name}={self.value} at {self.timestamp}>"
