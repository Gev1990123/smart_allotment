# utils/notifications.py
import utils.logger
import logging
import json
import os
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# == SETUP LOGGING ===
utils.logger.setup()

load_dotenv()

SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
TO_EMAIL = os.getenv('TO_EMAIL')

# Data Directory
ALERTS_DIR = os.path.join(os.path.dirname(__file__), '../data/alerts')
os.makedirs(ALERTS_DIR, exist_ok=True)
ALERTS_FILE = os.path.join(ALERTS_DIR, 'alerts.json')

def send_email_alert(subject, body, to_email):
    """
    Send an email alert.
    """
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = to_email

    # SMTP Settings
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        logging.info(f"✅ Email sent successfully: {subject}")
        return True
    
    except smtplib.SMTPAuthenticationError:
        logging.error("❌ Email FAILED - Invalid Gmail credentials")
        return False
    except smtplib.SMTPServerDisconnected:
        logging.error("❌ Email FAILED - Server disconnected (network issue)")
        return False
    except Exception as e:
        logging.error(f"❌ Email FAILED - {str(e)}")
        return False

def alert_low_moisture(sensor_name, value):
    """
    Alert for low soil moisture.
    """
    if not should_send_alert(sensor_name, 'low_soil_moisture'):
        logging.info(f"Low Soil Moisture Alert Skipped (cooldown active): {value}%")
        return

    subject = f"Alert: Low Moisture ({sensor_name})"
    body = f"Soil moisture is low: {value}%"
        
    # Send email
    send_email_alert(subject, body, TO_EMAIL)

    # Update alerts.json and mark as 'sent'
    mark_alert_sent(sensor_name, 'low_soil_moisture') 

def alert_high_temperature(sensor_name, value):
    """
    Alert for high temperature.
    """

    if not should_send_alert(sensor_name, 'high_temp'):
        logging.info(f"High Temp Alert Skipped (cooldown active): {value}°C")
        return

    subject = f"Alert: High Temperature ({sensor_name})"
    body = f"Temperature is high: {value}°C"
    
    # Send email
    send_email_alert(subject, body, TO_EMAIL)

    # Update alerts.json and mark as 'sent'
    mark_alert_sent(sensor_name, 'high_temp') 

def alert_low_temperature(sensor_name, value):
    """
    Alert for low temperature.
    """

    if not should_send_alert(sensor_name, 'low_temp'):
        logging.info(f"Low Temp Alert Skipped (cooldown active): {value}°C")
        return

    subject = f"Alert: Low Temperature ({sensor_name})"
    body = f"Temperature is Low: {value}°C"
    
    # Send email
    send_email_alert(subject, body, TO_EMAIL)

    # Update alerts.json and mark as 'sent'
    mark_alert_sent(sensor_name, 'low_temp') 

def alert_low_light(sensor_name, value):
    """
    Alert for low light.
    """

    logging.info(should_send_alert)

    if not should_send_alert(sensor_name, 'low_light'):
        logging.info(f"Low Light Alert Skipped (cooldown active): {value}°C")
        return

    subject = f"Alert: Low Light ({sensor_name})"
    body = f"Light is Low: {value} Lux"
    
    # Send email
    send_email_alert(subject, body, TO_EMAIL)

    # Update alerts.json and mark as 'sent'
    mark_alert_sent(sensor_name, 'low_light') 

def load_alerts():
    """Load last alert times from data/alerts/alerts.json."""
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_alerts(alerts):
    """Save alert times to data/alerts/alerts.json."""
    with open(ALERTS_FILE, 'w') as f:
        json.dump(alerts, f)

def should_send_alert(sensor_name, alert_type):
    alerts = load_alerts()
    key = f"{sensor_name}_{alert_type}"
    
    if key not in alerts:
        return True
    
    last_time = datetime.fromisoformat(alerts[key])
    if datetime.now() - last_time > timedelta(hours=4):
        return True
    return False

def mark_alert_sent(sensor_name, alert_type):
    alerts = load_alerts()
    key = f"{sensor_name}_{alert_type}"
    alerts[key] = datetime.now().isoformat()
    save_alerts(alerts)
