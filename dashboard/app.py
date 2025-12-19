import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, jsonify
from sensors import soil_moisture, temperature, light

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api/readings')
def readings():
    return jsonify({
        "soil_moisture": soil_moisture.read(),
        "temperature": temperature.read(),
        "light": light.read()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)