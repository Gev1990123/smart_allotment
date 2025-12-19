# utils/notifications.py
import logging
# import smtplib
# from email.message import EmailMessage

# Optional: email sending function (keep as-is)
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
    
    # Optionally send email
    # send_email_alert(subject, body, "you@example.com")