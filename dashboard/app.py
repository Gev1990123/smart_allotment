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
    return jsonify({
        "soil_moisture": soil_moisture.read(),
        "temperature": temperature.read(),
        "light": light.read()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)