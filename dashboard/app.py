import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
import time
from flask import Flask, render_template, jsonify
from models import db
from models.sensor_data import SensorReading
from models.alerts import Alert
from sensors import soil_moisture, temperature, light

LOW_MOISTURE_THRESHOLD = 30  # %

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'smart_allotment.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ---------------- Sensor Logging Loop ----------------
def log_readings_loop(interval=300):
    """Continuously log sensor readings and create alerts"""
    with app.app_context():
        while True:
            try:
                soil_val = soil_moisture.read()
                db.session.add(SensorReading(sensor_type='soil_moisture', value=soil_val))
                if soil_val < LOW_MOISTURE_THRESHOLD:
                    db.session.add(Alert(alert_type='Low Moisture', sensor_name='Soil', value=soil_val))
                db.session.commit()
            except Exception as e:
                print("Error logging soil:", e)

            try:
                temp_val = temperature.read()
                db.session.add(SensorReading(sensor_type='temperature', value=temp_val))
                db.session.commit()
            except Exception as e:
                print("Error logging temperature:", e)

            try:
                light_val = light.read()
                db.session.add(SensorReading(sensor_type='light', value=light_val))
                db.session.commit()
            except Exception as e:
                print("Error logging light:", e)

            time.sleep(interval)

# Start background thread
threading.Thread(target=log_readings_loop, daemon=True).start()

# ---------------- Dashboard Routes ----------------
@app.route('/')
def index():
    # latest readings from database
    with app.app_context():
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
    return jsonify([{"time": a.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                     "type": a.alert_type,
                     "sensor": a.sensor_name,
                     "value": a.value} for a in alerts])

@app.route('/api/readings')
def readings():
    soil = SensorReading.query.filter_by(sensor_type='soil_moisture').order_by(SensorReading.timestamp.desc()).first()
    temp = SensorReading.query.filter_by(sensor_type='temperature').order_by(SensorReading.timestamp.desc()).first()
    light_val = SensorReading.query.filter_by(sensor_type='light').order_by(SensorReading.timestamp.desc()).first()

    return jsonify({
        "soil_moisture": soil.value if soil else None,
        "soil_status": "Online" if soil else "Offline",
        "temperature": temp.value if temp else None,
        "temp_status": "Online" if temp else "Offline",
        "light": light_val.value if light_val else None,
        "light_status": "Online" if light_val else "Offline"
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)