#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
import time
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from models.db import db 
from models.sensor_data import SensorReading
from models.alerts import Alert
from sensors import soil_moisture, temperature, light
import utils.logger
import logging
from utils.notifications import alert_high_temperature, alert_low_light, alert_low_temperature, alert_low_moisture

# == SETUP LOGGING ===
utils.logger.setup()
logging.info("=== Smart Allotment Dashboard starting ===")

# === CREATE APP & DB HERE (eliminates circular imports) ===
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'smart_allotment.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# === INITIALIZE DB FROM db.py ===
db.init_app(app)

LOW_MOISTURE_THRESHOLD = 30  # %
HIGH_TEMP_THRESHOLD = 30 # °C
LOW_TEMP_THRESHOLD = 0 # °C
LOW_LIGHT_THRESHOLD = 2000 # Lux

def log_readings_loop(interval=30): #300 = 5mintues, changed to 30 for testing. 
    """Continuously log sensor readings and create alerts"""
    logging.info("Sensor logging loop started") 
    with app.app_context():
        while True:
            try:
                soil_val = soil_moisture.read()
                db.session.add(SensorReading(sensor_type='soil_moisture', value=soil_val))
                if soil_val < LOW_MOISTURE_THRESHOLD:                    
                    db.session.add(Alert(alert_type='Low Moisture', sensor_name='Soil', value=soil_val))
                    logging.warning(f"Low Moisture Detected {soil_val}%")
                    alert_low_moisture('Soil', soil_val)
                db.session.commit()
                logging.info(f"Soil moisture: {soil_val}%")
            except Exception as e:
                logging.error("Error logging soil:", e)

            try:
                temp_val = temperature.read()
                db.session.add(SensorReading(sensor_type='temperature', value=temp_val))
                if temp_val >= HIGH_TEMP_THRESHOLD:
                    db.session.add(Alert(alert_type='High Temperature', sensor_name='Temp', value=temp_val))
                    logging.warning(f"High Temperature Detected {temp_val}°C")
                    alert_high_temperature('Temp', temp_val)
                if temp_val <= LOW_TEMP_THRESHOLD:
                    db.session.add(Alert(alert_type='Low Temperature', sensor_name='Temp', value=temp_val))    
                    logging.warning(f"Low Temperature Detected {temp_val}°C")
                    alert_low_temperature('Temp', temp_val)
                db.session.commit()
                logging.info(f"Temperature: {temp_val}°C")
            except Exception as e:
                logging.error("Error logging temperature:", e)

            try:
                light_val = light.read()
                db.session.add(SensorReading(sensor_type='light', value=light_val))
                if light_val <= LOW_LIGHT_THRESHOLD:
                    db.session.add(Alert(alert_type='Low Light', sensor_name='Light', value=light_val))
                    logging.warning(f"Low Light Detected {light_val}")
                    alert_low_light('Light', light_val)
                db.session.commit()
                logging.info(f"Light Lux Value: {light_val} ")
            except Exception as e:
                logging.error("Error logging light:", e)

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
        "temperature": temp_data,
        "temp_labels": temp_labels,
        "temp_status": temp_status,
        "light": light_data,
        "light_labels": light_labels,
        "light_status": light_status
    })

# ---------------- STARTUP ----------------
if __name__ == '__main__':
    # Manual testing
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # Systemd service
    with app.app_context():
        db.create_all()
        logging.info("Smart Allotment Dashboard started on port 5000")
    
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, app, use_reloader=False)
