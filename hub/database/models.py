
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    JSON,
    ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

class Site(Base):
    """
    Represents an allotment site or plot.
    Each site may have multiple sensor devices (Raspberry Pis).
    """
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True)
    site_code = Column(String, unique=True, nullable=False)   # e.g. "plot01"
    friendly_name = Column(String)                            # Human readable name

    # Relationship: one site → many sensor readings
    readings = relationship("SensorData", back_populates="site")


class SensorData(Base):
    """
    Represents a single sensor reading from a device.
    This is the recommended long-table time-series structure:
    - One row per sensor reading
    - Flexible for adding new sensor types
    - Matches the MQTT ingest pipeline
    """
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True)

    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)

    device_id = Column(String, nullable=False)                 # Raspberry Pi or sensor device
    sensor_type = Column(String, nullable=False)               # e.g. "temperature", "soil_moisture"
    value = Column(Float, nullable=False)                      # numeric sensor reading
    unit = Column(String, nullable=True)                       # e.g. "%", "°C", "lux"

    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    raw = Column(JSON)                                         # full raw message payload

    # Relationship back to Site
    site = relationship("Site", back_populates="readings")
