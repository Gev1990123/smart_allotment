import smtplib
from email.message import EmailMessage


def send_email_alert(subject, body, to_email):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = 'smartallotment@example.com'
    msg['To'] = to_email

    # Note: replace with your SMTP settings
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('username', 'password')
        server.send_message(msg)

def alert_low_moisture(sensor_name, value):
    subject = f"Alert: Low Moisture ({sensor_name})"
    body = f"Soil moisture is low: {value}%"
    print(subject, body)  # Print to console/log
    # send_email_alert(subject, body, "you@example.com")

def alert_high_temperature(sensor_name, value):
    subject = f"Alert: High Temperature ({sensor_name})"
    body = f"Temperate is high: {value}%"
    print(subject, body)  # Print to console/log
    # send_email_alert(subject, body, "you@example.com")


