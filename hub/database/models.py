
from sqlalchemy import Column, Integer, Float, String, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Site(Base):
    __tablename__ = "sites"
    
    id = Column(Integer, primary_key=True)
    site_code = Column(String, unique=True, nullable=False)
    friendly_name = Column(String)

class Telemetry(Base):
    __tablename__ = "telemetry"
    
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("sites.id"))
    timestamp = Column(TIMESTAMP)
    
    soil_moisture = Column(Float)
    water_level = Column(Float)
    humidity = Column(Float)
    temperature = Column(Float)
    
    raw_json = Column(JSON)
    
    site = relationship("Site")
