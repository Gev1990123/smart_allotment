# utils/notifications.py
import logging
# import smtplib
# from email.message import EmailMessage

ALERTS = []  # Global list to keep alerts

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

def add_alert(alert_type, sensor_name, value):
    """Add an alert to the global list, keeping only the last 10."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ALERTS.append({"time": timestamp, "type": alert_type, "sensor": sensor_name, "value": value})
    if len(ALERTS) > 10:
        ALERTS.pop(0)  # Keep only last 10