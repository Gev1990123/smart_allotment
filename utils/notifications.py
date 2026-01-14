# utils/notifications.py
from utils.logger import setup
import logging
import os
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from flask import current_app
from models.db import db
from models.alerts import Alert

load_dotenv()

SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
TO_EMAIL = os.getenv('TO_EMAIL')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

## Setup Logging
setup("notifications.log")

# Type mapping
ALERT_TYPES = {
    'low_soil_moisture': 'Low Moisture',
    'high_temp': 'High Temperature', 
    'low_temp': 'Low Temperature',
    'low_light': 'Low Light'
}


def send_email_alert(subject, body, to_email=None, admin=False):
    """
    Send an email alert.
    """
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER

    recipient = ADMIN_EMAIL if admin else to_email
    msg['To'] = recipient

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
    
    if not should_send_alert(sensor_name, 'low_light'):
        logging.info(f"Low Light Alert Skipped (cooldown active): {value} Lux")
        return

    subject = f"Alert: Low Light ({sensor_name})"
    body = f"Light is Low: {value} Lux"
    
    # Send email
    send_email_alert(subject, body, TO_EMAIL)

    # Update alerts.json and mark as 'sent'
    mark_alert_sent(sensor_name, 'low_light') 

def should_send_alert(sensor_name, alert_type):
    # Check database for last notification 
    
    real_type = ALERT_TYPES.get(alert_type)
    logging.info(f"Checking cooldown: {sensor_name}/{alert_type} → {real_type}")
    if not real_type:
        logging.error(f"Unknown alert_type: {alert_type}")
        return False

    with current_app.app_context():
        # CHANGE: order_by(Alert.last_notified.desc()) → order_by(Alert.id.asc())
        last_alert = Alert.query.filter_by(
            sensor_name=sensor_name, 
            alert_type=real_type
        ).order_by(Alert.last_notified.desc()).first()
        
        if not last_alert or not last_alert.last_notified:
            logging.info("No previous alert found → SEND")
            return True
        
        hours_diff = (datetime.utcnow() - last_alert.last_notified).total_seconds() / 3600
        logging.info(f"Hours since last alert: {hours_diff:.1f}")
        return hours_diff > 4

def mark_alert_sent(sensor_name, alert_type):
    # Update LAST alert record with notification time

    real_type = ALERT_TYPES.get(alert_type)
    if not real_type:
        logging.error(f"Unknown alert_type: {alert_type}")
        return False

    with current_app.app_context():
        # Update ALL alerts for this sensor/type that haven't been notified
        result = Alert.query.filter_by(
            sensor_name=sensor_name, 
            alert_type=real_type
        ).filter(Alert.last_notified.is_(None)).update({
            Alert.last_notified: datetime.utcnow()
        })
        db.session.commit()
        logging.info(f"✅ Marked {result} alerts as notified: {sensor_name}/{real_type}")
        return result > 0