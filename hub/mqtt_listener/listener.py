import paho.mqtt.client as mqtt
import psycopg2
import json
from datetime import datetime
import os

# Database config
DB_HOST = os.getenv("PSQL_HOST", "database")
DB_PORT = os.getenv("PSQL_PORT", "5432")
DB_USER = os.getenv("PSQL_USER", "mqtt")
DB_PASS = os.getenv("PSQL_PASS", "mqtt123")
DB_NAME = os.getenv("PSQL_DB", "sensors")

# MQTT config  
MQTT_HOST = os.getenv("MQTT_HOST", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USERNAME", "matt")
MQTT_PASS = os.getenv("MQTT_PASSWORD", "mqtt123")

def connect_db():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, 
        password=DB_PASS, database=DB_NAME
    )

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker: {rc}")
    client.subscribe("sensors/+/data")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print(f"Received: {data} from {msg.topic}")
        
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sensor_data (device_id, timestamp, temperature, humidity, soil_moisture, location, battery_voltage)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            msg.topic.split('/')[1],           
            datetime.now(),                      
            data.get('temperature'),           
            data.get('humidity'),
            data.get('soil_moisture'),
            data.get('location'),
            data.get('battery_voltage')
        ))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
#client.tls_set(ca_certs="/listener/certs/ca.crt")
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_forever()