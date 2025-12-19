import sys
import json, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, jsonify
from sensors import soil_moisture, temperature, light

app = Flask(__name__)

ALERTS_FILE = "data/logs/alerts.json"

@app.route('/')
def index():
    # Get latest sensor readings
    soil = soil_moisture.read()
    temp = temperature.read()
    light_val = light.read()

    # Render dashboard template
    return render_template("index.html", soil=soil, temp=temp, light=light_val)

@app.route("/alerts")
def get_alerts():
    """Return only the last 10 alerts as JSON for the dashboard."""
    if os.path.exists(ALERTS_FILE):
        try:
            with open(ALERTS_FILE, "r") as f:
                alerts = json.load(f)
        except Exception:
            alerts = []
    else:
        alerts = []

    # Return only last 10 for live table
    return jsonify(alerts[-10:])

@app.route('/api/readings')
def readings():
    try:
        soil_val = soil_moisture.read()
        soil_status = "Online"
    except:
        soil_val = None
        soil_status = "Offline"

    try:
        temp_val = temperature.read()
        temp_status = "Online"
    except:
        temp_val = None
        temp_status = "Offline"

    try:
        light_val = light.read()
        light_status = "Online"
    except:
        light_val = None
        light_status = "Offline"

    return jsonify({
        "soil_moisture": soil_val,
        "soil_status": soil_status,
        "temperature": temp_val,
        "temp_status": temp_status,
        "light": light_val,
        "light_status": light_status
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)