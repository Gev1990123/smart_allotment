import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
import time
import fcntl
from app.extensions import db
from sensors import soil_moisture, temperature, light
from utils.logger import setup_logging, get_logger
from utils.notifications import alert_high_temperature, alert_low_light, alert_low_temperature, alert_low_moisture, should_send_alert
from models.sensor_data import SensorReading
from models.alerts import Alert

# Setup logging FIRST
setup_logging()
logger = get_logger("app")

LOW_MOISTURE_THRESHOLD = 30
HIGH_TEMP_THRESHOLD = 30
LOW_TEMP_THRESHOLD = 0
LOW_LIGHT_THRESHOLD = 2000
INTERVAL_SECS = int(os.getenv('INTERVAL', '60'))

def sensor_loop():
    """Single clean sensor loop - FIXED: 1 reading/probe/60s instead of 272/hour"""
    logger.info("Sensor logging loop started - OPTIMIZED for 60s intervals")
    
    while True:
        try:
            # STEP 1: READ ALL SENSORS FIRST (fast, memory only)
            soil_readings = soil_moisture.read_all()
            temp_readings = temperature.read_all()
            light_readings = light.read_all()

            # STEP 2: PROCESS ALL ALERTS FIRST (track changes, no readings yet)
            alerts_changed = False  # Track if we need to commit alerts
            
            # ===== SOIL MOISTURE ALERTS =====
            for probe_name, soil_val in soil_readings.items():
                # Skip if sensor failed to read (None = hardware/sensor error)
                if soil_val is None:
                    continue
                
                sensor_name = f"Soil-{probe_name.title()}"
                
                # Check if there's already an ACTIVE alert for this specific sensor
                existing_alert = Alert.query.filter_by(sensor_name=sensor_name, alert_type='Low Moisture', status='active').first()
                
                # THRESHOLD BREACH: soil_val <= LOW_MOISTURE_THRESHOLD
                if soil_val <= LOW_MOISTURE_THRESHOLD:
                    # FIRST TIME BREACH: No existing active alert found
                    if not existing_alert:
                        # Create new active alert record (this triggers first notification)
                        db.session.add(Alert(alert_type='Low Moisture', sensor_name=sensor_name, value=soil_val))
                        db.session.commit()
                        alert_low_moisture(sensor_name, soil_val)  # Send first notification immediately
                    else:
                        # ONGOING BREACH: Alert already exists, check 4hr notification cooldown
                        # should_send_alert() checks last_notified timestamp in Alert table
                        if should_send_alert(sensor_name, 'low_moisture'):
                            # 4+ hours passed → Send email notification
                            alert_low_moisture(sensor_name, soil_val)

                # CONDITION RESOLVED: Reading now normal AND alert was active
                elif existing_alert and soil_val > LOW_MOISTURE_THRESHOLD:
                    # Problem fixed → Mark alert as resolved (stops future notifications)
                    existing_alert.status = 'resolved'
                    db.session.commit()

            # ===== TEMPERATURE ALERTS =====
            for probe_name, temp_val in temp_readings.items():
                # Skip if sensor failed to read (None = hardware/sensor error)
                if temp_val is None:
                    continue
                
                sensor_name = f"Temp-{probe_name.title()}"
                
                # Check existing alerts
                high_alert = Alert.query.filter_by(sensor_name=sensor_name, alert_type='High Temperature', status='active').first()
                low_alert = Alert.query.filter_by(sensor_name=sensor_name, alert_type='Low Temperature', status='active').first()
                
                # THRESHOLD BREACH: temp_val >= HIGH_TEMP_THRESHOLD (e.g., <= 50 lux)
                if temp_val >= HIGH_TEMP_THRESHOLD:
                    # FIRST TIME BREACH: No existing active alert found
                    if not high_alert:
                        # Create new active alert record (this triggers first notification via should_send_alert)
                        db.session.add(Alert(alert_type='High Temperature', sensor_name=sensor_name, value=temp_val))
                        db.session.commit()
                        alert_high_temperature(sensor_name, temp_val)  #Send first notification immediedatley 
                    else:
                        # ONGOING BREACH: Alert already exists, check 4hr notification cooldown
                        # should_send_alert() checks last_notified timestamp in Alert table
                        if should_send_alert(sensor_name, 'high_temp'):
                            # 4+ hours passed → Send email notification
                            alert_high_temperature(sensor_name, temp_val)

                # CONDITION RESOLVED: Reading now normal AND alert was active
                elif high_alert and temp_val < HIGH_TEMP_THRESHOLD:
                    # Problem fixed → Mark alert as resolved (stops future notifications)
                    high_alert.status = 'resolved'
                    db.session.commit()
                
                # THRESHOLD BREACH: temp_val >= HIGH_TEMP_THRESHOLD (e.g., <= 50 lux)
                if temp_val <= LOW_TEMP_THRESHOLD:
                    # FIRST TIME BREACH: No existing active alert found
                    if not low_alert:
                        # Create new active alert record (this triggers first notification via should_send_alert)
                        db.session.add(Alert(alert_type='Low Temperature', sensor_name=sensor_name, value=temp_val))
                        db.session.commit()
                        alert_low_temperature(sensor_name, temp_val) #Send first notification immediedatley 
                    else:
                        # ONGOING BREACH: Alert already exists, check 4hr notification cooldown
                        # should_send_alert() checks last_notified timestamp in Alert table
                        if should_send_alert(sensor_name, 'low_temp'):
                            # 4+ hours passed → Send email notification
                            alert_low_temperature(sensor_name, temp_val)
                
                # CONDITION RESOLVED: Reading now normal AND alert was active
                elif low_alert and temp_val > LOW_TEMP_THRESHOLD:
                    # Problem fixed → Mark alert as resolved (stops future notifications)
                    low_alert.status = 'resolved'
                    db.session.commit()

            # ===== LIGHT ALERTS =====
            for probe_name, light_val in light_readings.items():
                # Skip if sensor failed to read (None = hardware/sensor error)
                if light_val is None:
                    continue

                # Create consistent sensor name: "Light-Probe1", "Light-Probe2", etc.
                sensor_name = f"Light-{probe_name.title()}"

                # Check if there's already an ACTIVE alert for this specific sensor/light condition
                existing_alert = Alert.query.filter_by(sensor_name=sensor_name, alert_type='Low Light', status='active').first()
                
                # THRESHOLD BREACH: light_val <= LOW_LIGHT_THRESHOLD
                if light_val <= LOW_LIGHT_THRESHOLD:
                    # FIRST TIME BREACH: No existing active alert found
                    if not existing_alert:
                        # Create new active alert record (this triggers first notification)
                        db.session.add(Alert(alert_type='Low Light', sensor_name=sensor_name, value=light_val))
                        db.session.commit()
                        alert_low_light(sensor_name, light_val)  # Send first notification immediately 
                    else: 
                        # ONGOING BREACH: Alert already exists, check 4hr notification cooldown
                        if should_send_alert(sensor_name, 'low_light'):
                            # 4+ hours passed → Send email notification
                            alert_low_light(sensor_name, light_val)

                # CONDITION RESOLVED: Reading now normal AND alert was active
                elif existing_alert and light_val >= LOW_LIGHT_THRESHOLD:
                    # Problem fixed → Mark alert as resolved (stops future notifications)
                    existing_alert.status = 'resolved'
                    db.session.commit()
            

            # ========================================
            # STEP 3: NOW log ALL sensor readings (batch, memory only)
            # ========================================
            reading_count = 0
            
            # SOIL readings (ALWAYS log every reading to SensorReading table - complete history)
            for probe_name, soil_val in soil_readings.items():
                if soil_val is not None:
                    db.session.add(SensorReading(sensor_type='soil_moisture', value=soil_val, probe_id=probe_name))
                    reading_count += 1
            
            # TEMPERATURE readings (ALWAYS log every reading to SensorReading table - complete history)
            for probe_name, temp_val in temp_readings.items():
                if temp_val is not None:
                    db.session.add(SensorReading(sensor_type='temperature', value=temp_val, probe_id=probe_name))
                    reading_count += 1
            
            # LIGHT readings (ALWAYS log every reading to SensorReading table - complete history)
            for probe_name, light_val in light_readings.items():
                if light_val is not None:
                    db.session.add(SensorReading(sensor_type='light', value=light_val, probe_id=probe_name))
                    reading_count += 1
            
            # ========================================
            # STEP 4: SINGLE COMMIT for ALL readings (fast!)
            # ========================================
            db.session.commit()
            logger.info(f"Sensor cycle complete: {reading_count} readings saved every {INTERVAL_SECS}s")

        except Exception as e:
            # Rollback on any error
            db.session.rollback()
            logger.error(f"Sensor loop error: {e}")
        
        # ========================================
        # STEP 6: SLEEP - NOW TRULY 60s intervals (fixes 272→60 readings/hour)
        # ========================================
        logger.debug(f"Sleeping {INTERVAL_SECS}s until next cycle...")
        time.sleep(INTERVAL_SECS)

def start_sensor_loop(app):
    """Start daemon thread safely"""
    # Push app context for thread

    lock_file_path = '/tmp/sensor_loop.lock'
    lock_file = None

    try:
        lock_file = open(lock_file_path, 'w')
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        logger.info("Sensor loop lock acquired - starting SINGLE instance")
    except IOError:
        logger.info("Sensor loop already running elsewhere - SKIPPING")
        return  # EXIT - don't start duplicate!


    def run_in_context():
        try:
            with app.app_context():
                sensor_loop()
        finally:
            # Cleanup lock on exit (optional - file stays for restart protection)
            if lock_file:
                try:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                    lock_file.close()
                    os.unlink(lock_file_path)
                except:
                    pass

        
    thread = threading.Thread(target=run_in_context, daemon=True)
    thread.start()
    logger.info("Sensor background thread started")