#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
import time
from app.extensions import db
from sensors import soil_moisture, temperature, light
from utils.logger import setup_logging, get_logger
from utils.notifications import alert_high_temperature, alert_low_light, alert_low_temperature, alert_low_moisture, should_send_alert
from models.sensor_data import SensorReading
from models.alerts import Alert

# Setup logging FIRST
setup_logging()
logger = get_logger("sensor_loop")

LOW_MOISTURE_THRESHOLD = 30
HIGH_TEMP_THRESHOLD = 30
LOW_TEMP_THRESHOLD = 0
LOW_LIGHT_THRESHOLD = 2000
INTERVAL_SECS = int(os.getenv('INTERVAL', '60'))

def sensor_loop():
    """Single clean sensor loop - NO NESTING"""
    logger.info("Sensor logging loop started")
    
    while True:
        try:
            # SOIL
            soil_readings = soil_moisture.read_all()
            for probe_name, soil_val in soil_readings.items():
                if soil_val is None:
                    continue
                sensor_name = f"Soil-{probe_name.title()}"
                
                # Log reading
                db.session.add(SensorReading(sensor_type='soil_moisture', value=soil_val, probe_id=probe_name))
                
                # Alert logic (YOUR ORIGINAL CODE - perfect)
                existing_alert = Alert.query.filter_by(sensor_name=sensor_name, alert_type='Low Moisture', status='active').first()
                if soil_val <= LOW_MOISTURE_THRESHOLD:
                    if not existing_alert:
                        db.session.add(Alert(alert_type='Low Moisture', sensor_name=sensor_name, value=soil_val))
                        db.session.commit()
                        logger.warning(f"Low Moisture Detected {soil_val}%")
                    alert_low_moisture(sensor_name, soil_val)
                elif existing_alert and soil_val > LOW_MOISTURE_THRESHOLD:
                    existing_alert.status = 'resolved'
                    db.session.commit()
                    logger.info(f"Low Moisture RESOLVED: {soil_val}")
                db.session.commit()
                logger.info(f"Soil moisture: {soil_val}%")

            # TEMP (YOUR ORIGINAL LOGIC - perfect)
            temp_readings = temperature.read_all()
            for probe_name, temp_val in temp_readings.items():
                if temp_val is None:
                    continue
                sensor_name = f"Temp-{probe_name.title()}"
                db.session.add(SensorReading(sensor_type='temperature', value=temp_val, probe_id=probe_name))
                
                high_alert = Alert.query.filter_by(sensor_name=sensor_name, alert_type='High Temperature', status='active').first()
                low_alert = Alert.query.filter_by(sensor_name=sensor_name, alert_type='Low Temperature', status='active').first()
                
                if temp_val >= HIGH_TEMP_THRESHOLD:
                    if not high_alert:
                        db.session.add(Alert(alert_type='High Temperature', sensor_name=sensor_name, value=temp_val))
                        db.session.commit()
                    alert_high_temperature(sensor_name, temp_val)
                elif high_alert and temp_val < HIGH_TEMP_THRESHOLD:
                    high_alert.status = 'resolved'
                    db.session.commit()
                
                if temp_val <= LOW_TEMP_THRESHOLD:
                    if not low_alert:
                        db.session.add(Alert(alert_type='Low Temperature', sensor_name=sensor_name, value=temp_val))
                        db.session.commit()
                    alert_low_temperature(sensor_name, temp_val)
                elif low_alert and temp_val > LOW_TEMP_THRESHOLD:
                    low_alert.status = 'resolved'
                    db.session.commit()
                db.session.commit()

            # LIGHT
            # Take a reading from all light sensors
            light_readings = light.read_all()

            # Loop through each sensor reading (probe_name = sensor ID, light_val = lux reading)
            for probe_name, light_val in light_readings.items():
                # Skip if sensor failed to read (None = hardware/sensor error)
                if light_val is None:
                    continue

                # Create consistent sensor name: "Light-Probe1", "Light-Probe2", etc.
                sensor_name = f"Light-{probe_name.title()}"

                # ALWAYS log every reading to SensorReading table (complete history)
                db.session.add(SensorReading(sensor_type='light', value=light_val, probe_id=probe_name))
                
                # Check if there's already an ACTIVE alert for this specific sensor/light condition
                # This query ignores reading value - only cares about alert state
                existing_alert = Alert.query.filter_by(sensor_name=sensor_name, alert_type='Low Light', status='active').first()
                
                # THRESHOLD BREACH: light_val <= LOW_LIGHT_THRESHOLD (e.g., <= 50 lux)
                if light_val <= LOW_LIGHT_THRESHOLD:
                    # FIRST TIME BREACH: No existing active alert found
                    if not existing_alert:
                        # Create new active alert record (this triggers first notification via should_send_alert)
                        db.session.add(Alert(alert_type='Low Light', sensor_name=sensor_name, value=light_val))
                        # Commit immediately so alert appears in DB for next checks
                        db.session.commit()
                        alert_low_light(sensor_name, light_val)  #Send first notification immediedatley 
                    else: 
                        # ONGOING BREACH: Alert already exists, check 4hr notification cooldown
                        # should_send_alert() checks last_notified timestamp in Alert table
                        if should_send_alert(sensor_name, 'low_light'):
                            # 4+ hours passed → Send email notification
                            alert_low_light(sensor_name, light_val)

                # CONDITION RESOLVED: Reading now normal AND alert was active
                elif existing_alert and light_val >= LOW_LIGHT_THRESHOLD:
                    # Problem fixed → Mark alert as resolved (stops future notifications)
                    existing_alert.status = 'resolved'
                    db.session.commit()

                 # Final commit for SensorReading + any other changes    
                db.session.commit()

            logger.info(f"Sensor cycle complete. Sleeping {INTERVAL_SECS}s")
            
        except Exception as e:
            logger.error(f"Sensor loop error: {e}")
        
        time.sleep(INTERVAL_SECS)

def start_sensor_loop(app):
    """Start daemon thread safely"""
    # Push app context for thread
    def run_in_context():
        with app.app_context():
            sensor_loop()
    
    thread = threading.Thread(target=run_in_context, daemon=True)
    thread.start()
    logger.info("Sensor background thread started")