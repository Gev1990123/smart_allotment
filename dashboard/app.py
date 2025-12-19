import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, jsonify
from sensors import soil_moisture, temperature, light
from utils.notifications import ALERTS

app = Flask(__name__)

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
    """Return the last alerts as JSON"""
    return jsonify(ALERTS)

@app.route('/api/readings')
def readings():
    return jsonify({
        "soil_moisture": soil_moisture.read(),
        "temperature": temperature.read(),
        "light": light.read()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)