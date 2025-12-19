# utils/notifications.py
import logging
import json
import os
from datetime import datetime
# import smtplib
# from email.message import EmailMessage

ALERTS_FILE = "data/logs/alerts.json"

def send_email_alert(subject, body, to_email):
    """
    Send an email alert.
    """
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = 'smartallotment@example.com'
    msg['To'] = to_email

    # Replace with your SMTP settings
    # with smtplib.SMTP('smtp.example.com', 587) as server:
    #     server.starttls()
    #     server.login('username', 'password')
    #     server.send_message(msg)

def alert_low_moisture(sensor_name, value):
    """
    Alert for low soil moisture.
    """
    subject = f"Alert: Low Moisture ({sensor_name})"
    body = f"Soil moisture is low: {value}%"
    
    # Print to console
    print(subject, body)
    
    # Log to app.log
    logging.warning(f"{subject} - {body}")

    # Add Alert
    add_alert("Low Moisture", sensor_name, value)
    
    # Optionally send email
    # send_email_alert(subject, body, "you@example.com")

def alert_high_temperature(sensor_name, value):
    """
    Alert for high temperature.
    """
    subject = f"Alert: High Temperature ({sensor_name})"
    body = f"Temperature is high: {value}°C"
    
    # Print to console
    print(subject, body)
    
    # Log to app.log
    logging.warning(f"{subject} - {body}")

    # Add Alert
    add_alert("High Temperature", sensor_name, value)
    
    # Optionally send email
    # send_email_alert(subject, body, "you@example.com")


def _load_alerts():
    """Load all alerts from the JSON file."""
    if not os.path.exists(ALERTS_FILE):
        return []
    try:
        with open(ALERTS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def _save_alert(alert):
    """Append a new alert to the file."""
    alerts = _load_alerts()
    alerts.append(alert)  # keep all alerts
    os.makedirs(os.path.dirname(ALERTS_FILE), exist_ok=True)
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=2)

def add_alert(alert_type, sensor_name, value):
    """Add a new alert (stored permanently)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert = {
        "time": timestamp,
        "type": alert_type,
        "sensor": sensor_name,
        "value": value
    }
    _save_alert(alert)