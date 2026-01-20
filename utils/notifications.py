# utils/notifications.py
from utils.logger import get_logger
import logging
import os
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from flask import current_app
from app.extensions import db
from models.alerts import Alert

load_dotenv()

SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
TO_EMAIL = os.getenv('TO_EMAIL')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

## Setup Logging
logger = get_logger("notifications")

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
        logger.info(f"✅ Email sent successfully: {subject}")
        return True
    
    except smtplib.SMTPAuthenticationError:
        logger.error("❌ Email FAILED - Invalid Gmail credentials")
        return False
    except smtplib.SMTPServerDisconnected:
        logger.error("❌ Email FAILED - Server disconnected (network issue)")
        return False
    except Exception as e:
        logger.error(f"❌ Email FAILED - {str(e)}")
        return False

def alert_low_moisture(sensor_name, value):
    """
    Alert for low soil moisture.
    """
    if not should_send_alert(sensor_name, 'low_soil_moisture'):
        logger.info(f"Low Soil Moisture Alert Skipped (cooldown active): {value}%")
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
        logger.info(f"High Temp Alert Skipped (cooldown active): {value}°C")
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
        logger.info(f"Low Temp Alert Skipped (cooldown active): {value}°C")
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
    
    subject = f"Alert: Low Light ({sensor_name})"
    body = f"Light is Low: {value} Lux"
    
    # Send email
    send_email_alert(subject, body, TO_EMAIL)

    # Update Alerts Table and mark as 'sent'
    mark_alert_sent(sensor_name, 'low_light') 

def should_send_alert(sensor_name, alert_type):
    """
    Determines if email notification should be sent based on 4hr cooldown.
    Returns True if no previous notification or 4+ hours passed.
    """
    # Map internal alert_type key (e.g. 'low_light') to Alert table value (e.g. 'Low Light')
    # ALERT_TYPES = {'low_light': 'Low Light', 'low_soil_moisture': 'Low Moisture', ...}
    real_type = ALERT_TYPES.get(alert_type)

    # Log which sensor/alert combo we're checking for debugging
    logger.info(f"Checking cooldown: {sensor_name}/{alert_type} → {real_type}")

    # Validate alert type exists in our mapping - prevent invalid alerts
    if not real_type:
        logger.error(f"Unknown alert_type: {alert_type}")
        return False # Don't send email for unknown types

    # Create Flask app context to access database (required for Flask-SQLAlchemy)
    with current_app.app_context():

        # Find most recent ACTIVE alert that has been notified (last_notified not null)
        # Filters: exact sensor + alert type + has notification timestamp
        # Orders by newest notification first
        last_notified_alert = Alert.query.filter_by(
            sensor_name=sensor_name, 
            alert_type=real_type
        ).filter(Alert.last_notified.isnot(None)).order_by(
            Alert.last_notified.desc()
        ).first()
       
        # No previous notifications found → Send first alert immediately
        if not last_notified_alert or not last_notified_alert.last_notified:
            logger.info("No previous alert found → SEND EMAIL")
            return True

        # Calculate hours since last notification
        # datetime.utcnow() - last_notified = timedelta → total_seconds() / 3600 = hours
        hours_diff = (datetime.utcnow() - last_notified_alert.last_notified).total_seconds() / 3600

        # Log for debugging - shows exactly how long since last email
        logger.info(f"Hours since last alert: {hours_diff:.1f}")

        # Return True if 4+ hours passed (allows email), False if still in cooldown
        return hours_diff > 4

def mark_alert_sent(sensor_name, alert_type):
    """
    Updates the active Alert record with current notification timestamp.
    Called after successfully sending email to start 4hr cooldown period.
    """

    # Map internal alert_type key (e.g. 'low_light') to Alert table value (e.g. 'Low Light')
    # ALERT_TYPES = {'low_light': 'Low Light', 'low_soil_moisture': 'Low Moisture', ...}
    real_type = ALERT_TYPES.get(alert_type)

    # Validate alert type mapping exists - prevent database errors
    if not real_type:
        logger.error(f"Unknown alert_type: {alert_type}")
        return False # Fail silently, don't crash notification flow

    # Create Flask app context for database access (required by Flask-SQLAlchemy)
    with current_app.app_context():
        # Try to find MOST RECENT ACTIVE alert that was previously notified
        # Filters: exact sensor + alert type + active status + has notification timestamp
        # Orders by newest notification first (matches should_send_alert logic)
        # FIRST: Try to find most recent ACTIVE + PREVIOUSLY notified alert
        notified_alert = Alert.query.filter_by(
            sensor_name=sensor_name, 
            alert_type=real_type,
            status='active' 
        ).filter(Alert.last_notified.isnot(None)).order_by(
            Alert.last_notified.desc()
        ).first()

        # If we found a previously notified active alert, update its timestamp
        if notified_alert:
            # Set current UTC timestamp to start new 4hr cooldown period
            notified_alert.last_notified = datetime.utcnow()
            # Save changes to database
            db.session.commit()
            # Log success with alert ID for debugging
            logger.info(f"Updated repeat alert #{notified_alert.id}")
            return True
        
        # SECOND: No previously notified alert? Find most recent ACTIVE alert
        # This handles FIRST-TIME alerts (last_notified=NULL)
        first_alert = Alert.query.filter_by(
            sensor_name=sensor_name, 
            alert_type=real_type,
            status='active'
        ).order_by(Alert.id.desc()).first()
        
        if first_alert:
            # Set first notification timestamp on newly created alert
            first_alert.last_notified = datetime.utcnow()
            db.session.commit()
            logger.info(f"Set first notification on alert #{first_alert.id}")
            return True


        # No active alert found (shouldn't happen if should_send_alert passed)
        logger.info(f"No recent unnotified alert found")
        return False