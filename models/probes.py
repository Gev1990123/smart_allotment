from datetime import datetime
from . import db

class Probe(db.Model):
    __tablename__ = 'probes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    sensor_type = db.Column(db.String(20), nullable=False)  # 'soil', 'temp', 'light'
    channel = db.Column(db.String(10), nullable=False)      # 'A0', 'GPIO4', 'I2C-0x23'
    
    # Soil-specific (NULL for temp/light)
    dry_voltage = db.Column(db.Float, nullable=True)        # Soil only
    wet_voltage = db.Column(db.Float, nullable=True)        # Soil only
    
    # Threshold ranges
    min_value = db.Column(db.Float, nullable=True)          # Temp/light thresholds
    max_value = db.Column(db.Float, nullable=True)
    
    description = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)