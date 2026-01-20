from flask import Blueprint, render_template, jsonify
from app.extensions import db 
from models.sensor_data import SensorReading
from models.alerts import Alert
from utils.sensor_utils import format_light_level, format_moisture, format_temperature

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    soil = SensorReading.query.filter_by(sensor_type='soil_moisture').order_by(SensorReading.timestamp.desc()).first()
    temp = SensorReading.query.filter_by(sensor_type='temperature').order_by(SensorReading.timestamp.desc()).first()
    light_val = SensorReading.query.filter_by(sensor_type='light').order_by(SensorReading.timestamp.desc()).first()
    
    return render_template("index.html",
                          soil=soil.value if soil else None,
                          temp=temp.value if temp else None,
                          light=light_val.value if light_val else None)

@main_bp.route("/alerts")
def get_alerts():
    alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(10).all()
    return jsonify([{
        "time": a.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "type": a.alert_type,
        "sensor": a.sensor_name,
        "value": a.value
    } for a in alerts])

@main_bp.route('/api/readings')
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
