#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
import time
from flask import Flask, render_template, jsonify, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models.db import db 
from models.sensor_data import SensorReading
from models.alerts import Alert
from models.probes import Probe
from sensors import soil_moisture, temperature, light
import utils.logger
import logging
from dotenv import load_dotenv
from utils.notifications import alert_high_temperature, alert_low_light, alert_low_temperature, alert_low_moisture
from utils.sensor_utils import format_light_level, format_moisture, format_temperature

# == SETUP LOGGING ===
utils.logger.setup()
logging.info("=== Smart Allotment Dashboard starting ===")

# === Load ENV ===
load_dotenv()

# === CREATE APP & DB HERE (eliminates circular imports) ===
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_pre_ping': True,
    'pool_recycle': 3600
}
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-dev-secret')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# === INITIALIZE DB FROM db.py ===
db.init_app(app)

LOW_MOISTURE_THRESHOLD = 30  # %
HIGH_TEMP_THRESHOLD = 30 # °C
LOW_TEMP_THRESHOLD = 0 # °C
LOW_LIGHT_THRESHOLD = 2000 # Lux

def log_readings_loop(interval=3000): #300 = 5mintues, changed to 30 for testing. 
    """Continuously log sensor readings and create alerts"""
    logging.info("Sensor logging loop started") 
    with app.app_context():
        while True:
            try:
                soil_readings = soil_moisture.read_all() 

                for probe_name, soil_val in soil_readings.items():
                    if soil_val is None:
                        continue

                    # Probe-specific sensor name
                    sensor_name = f"Soil-{probe_name.title()}"  
                    db.session.add(SensorReading(sensor_type='soil_moisture', value=soil_val, probe_id=probe_name))


                    # CHECK if already alerting
                    existing_alert = Alert.query.filter_by(sensor_name=sensor_name, alert_type='Low Moisture', status='active').first()

                    if soil_val <= LOW_MOISTURE_THRESHOLD:  
                        if not existing_alert:
                            db.session.add(Alert(alert_type='Low Moisture', sensor_name=sensor_name, value=soil_val))
                            db.session.commit()
                            logging.warning(f"Low Moisture Detected {soil_val}%")
                                    
                        alert_low_moisture(sensor_name, soil_val)

                    elif existing_alert and soil_val > LOW_MOISTURE_THRESHOLD:
                        existing_alert.status = 'resolved'
                        db.session.commit()
                        logging.info(f"Low Moisture RESOLVED: {soil_val}")

                    db.session.commit()
                    logging.info(f"Soil moisture: {soil_val}%")
                
            except Exception as e:
                logging.error("Error logging soil: {e}")

            try:
                temp_val = temperature.read()
                sensor_name = 'Temp'
                db.session.add(SensorReading(sensor_type='temperature', value=temp_val))

                # CHECK if already alerting
                high_existing_alert = Alert.query.filter_by(sensor_name=sensor_name, alert_type='High Temperature', status='active').first()
                low_existing_alert = Alert.query.filter_by(sensor_name=sensor_name, alert_type='Low Temperature', status='active').first()

                if temp_val >= HIGH_TEMP_THRESHOLD:
                    if not high_existing_alert:
                        db.session.add(Alert(alert_type='High Temperature', sensor_name=sensor_name, value=temp_val))
                        db.session.commit()
                        logging.warning(f"High Temperature Detected {temp_val}°C")
                    
                    alert_high_temperature(sensor_name, temp_val)

                elif high_existing_alert and temp_val <= HIGH_TEMP_THRESHOLD:
                    high_existing_alert.status = 'resolved'
                    db.session.commit()
                    logging.info(f"High Temperature RESOLVED: {temp_val}")

                if temp_val <= LOW_TEMP_THRESHOLD:
                    if not low_existing_alert:
                        db.session.add(Alert(alert_type='Low Temperature', sensor_name=sensor_name, value=temp_val))    
                        db.session.commit()
                        logging.warning(f"Low Temperature Detected {temp_val}°C")

                    alert_low_temperature(sensor_name, temp_val)

                elif low_existing_alert and temp_val > HIGH_TEMP_THRESHOLD:
                    low_existing_alert.status = 'resolved'
                    db.session.commit()
                    logging.info(f"Low Temperature RESOLVED: {temp_val}")

                db.session.commit()
                logging.info(f"Temperature: {temp_val}°C")
            except Exception as e:
                logging.error("Error logging temperature: {e}")

            try:
                light_val = light.read()
                sensor_name = 'Light'
                db.session.add(SensorReading(sensor_type='light', value=light_val))
                
                # CHECK if already alerting
                existing_alert = Alert.query.filter_by(sensor_name=sensor_name, alert_type='Low Light', status='active').first()


                if light_val <= LOW_LIGHT_THRESHOLD:
                    if not existing_alert:
                        db.session.add(Alert(alert_type='Low Light', sensor_name=sensor_name, value=light_val))
                        db.session.commit()
                        logging.warning(f"NEW Low Light Alert: {light_val}")


                    alert_low_light(sensor_name, light_val)

                elif existing_alert and light_val > LOW_LIGHT_THRESHOLD:
                    existing_alert.status = 'resolved'
                    db.session.commit()
                    logging.info(f"Low Light RESOLVED: {light_val}")

                db.session.commit()
                logging.info(f"Light: {light_val}")

            except Exception as e:
                logging.error(f"Error logging light: {e}")

            time.sleep(interval)

# Start background thread
threading.Thread(target=log_readings_loop, daemon=True).start()

# ---------------- ROUTES ----------------
@app.route('/')
def index():
    soil = SensorReading.query.filter_by(sensor_type='soil_moisture').order_by(SensorReading.timestamp.desc()).first()
    temp = SensorReading.query.filter_by(sensor_type='temperature').order_by(SensorReading.timestamp.desc()).first()
    light_val = SensorReading.query.filter_by(sensor_type='light').order_by(SensorReading.timestamp.desc()).first()

    return render_template("index.html",
                          soil=soil.value if soil else None,
                          temp=temp.value if temp else None,
                          light=light_val.value if light_val else None)

@app.route("/alerts")
def get_alerts():
    alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(10).all()
    return jsonify([{
        "time": a.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "type": a.alert_type,
        "sensor": a.sensor_name,
        "value": a.value
    } for a in alerts])

@app.route('/api/readings')
def readings():
    N = 20
    soil_vals = SensorReading.query \
        .filter_by(sensor_type='soil_moisture') \
        .order_by(SensorReading.timestamp.desc()) \
        .limit(N).all()[::-1]

    temp_vals = SensorReading.query \
        .filter_by(sensor_type='temperature') \
        .order_by(SensorReading.timestamp.desc()) \
        .limit(N).all()[::-1]

    light_vals = SensorReading.query \
        .filter_by(sensor_type='light') \
        .order_by(SensorReading.timestamp.desc()) \
        .limit(N).all()[::-1]

    # Current values (latest readings)
    soil_current = soil_vals[-1].value if soil_vals else None
    temp_current = temp_vals[-1].value if temp_vals else None
    light_current = light_vals[-1].value if light_vals else None

    soil_data = [r.value for r in soil_vals]
    soil_labels = [r.timestamp.strftime("%H:%M:%S") for r in soil_vals]
    temp_data = [r.value for r in temp_vals]
    temp_labels = [r.timestamp.strftime("%H:%M:%S") for r in temp_vals]
    light_data = [r.value for r in light_vals]
    light_labels = [r.timestamp.strftime("%H:%M:%S") for r in light_vals]

    soil_status = "Online" if soil_vals and soil_vals[-1].timestamp else "Offline"
    temp_status = "Online" if temp_vals and temp_vals[-1].timestamp else "Offline"
    light_status = "Online" if light_vals and light_vals[-1].timestamp else "Offline"

    return jsonify({
        "soil_moisture": soil_data,
        "soil_labels": soil_labels,
        "soil_status": soil_status,
        "soil_current":format_moisture(soil_current),
        "temperature": temp_data,
        "temp_labels": temp_labels,
        "temp_status": temp_status,
        "temp_current": format_temperature(temp_current),
        "light": light_data,
        "light_labels": light_labels,
        "light_status": light_status,
        "light_current": format_light_level(light_current)
    })

@app.route('/probes')
def probe_dashboard():
    """Web interface to manage ALL probes"""
    probes = Probe.query.order_by(Probe.sensor_type, Probe.name).all()
    return render_template('probes.html', probes=probes)

@app.route('/probes/add', methods=['POST'])
def add_probe():
    """Add new probe via web form"""
    name = request.form['name']
    sensor_type = request.form['sensor_type']
    channel = request.form['channel']
    
    probe = Probe(
        name=name,
        sensor_type=sensor_type,
        channel=channel,
        description=request.form.get('description', ''),
        active=True
    )
    
    # ALL SENSORS: Thresholds (ALERT bounds)
    min_val = request.form.get('min_value', '').strip()
    max_val = request.form.get('max_value', '').strip()
    if min_val: probe.min_value = float(min_val)  # All sensors
    if max_val: probe.max_value = float(max_val)  # All sensors

    # Soil-specific calibration
    if sensor_type == 'soil':
        dry_voltage = request.form.get('dry_voltage', '').strip()
        wet_voltage = request.form.get('wet_voltage', '').strip()
        if dry_voltage: probe.dry_voltage = float(dry_voltage)
        if wet_voltage: probe.wet_voltage = float(wet_voltage)

    db.session.add(probe)
    db.session.commit()
    flash(f'Probe "{name}" added!')
    return redirect(url_for('probe_dashboard'))

@app.route('/probes/<name>/toggle')
def toggle_probe(name):
    """Toggle probe active/inactive"""
    probe = Probe.query.filter_by(name=name).first_or_404()
    probe.active = not probe.active
    db.session.commit()
    status = 'activated' if probe.active else 'deactivated'
    flash(f'Probe "{name}" {status}!')
    return redirect(url_for('probe_dashboard'))

@app.route('/probes/<name>/delete')
def delete_probe(name):
    """Delete probe"""
    probe = Probe.query.filter_by(name=name).first_or_404()
    db.session.delete(probe)
    db.session.commit()
    flash(f'Probe "{name}" deleted!')
    return redirect(url_for('probe_dashboard'))

# ---------------- STARTUP ----------------
if __name__ == '__main__':
    # Manual testing
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('DEBUG', 'False').lower() == 'true')
else:
    # Systemd service
    with app.app_context():
        db.create_all()
        logging.info("Smart Allotment Dashboard started on port 5000")
    
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, app, use_reloader=False)
