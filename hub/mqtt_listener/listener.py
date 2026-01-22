import json
import ssl
import time
import psycopg2
from psycopg2.extras import Json
import paho.mqtt.client as mqtt
import yaml
from datetime import datetime, timezone

# ---------------------------------------------------------
# Load configuration
# ---------------------------------------------------------

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

MQTT_HOST = config["mqtt"]["host"]
MQTT_PORT = config["mqtt"]["port"]
MQTT_USERNAME = config["mqtt"]["username"]
MQTT_PASSWORD = config["mqtt"]["password"]
MQTT_CA = config["mqtt"]["ca_cert"]
MQTT_TOPICS = config["mqtt"]["topics"]

PSQL_HOST = config["postgres"]["host"]
PSQL_PORT = config["postgres"]["port"]
PSQL_USER = config["postgres"]["user"]
PSQL_PASS = config["postgres"]["password"]
PSQL_DB   = config["postgres"]["db"]

# ---------------------------------------------------------
# PostgreSQL Connection
# ---------------------------------------------------------

def connect_psql():
    while True:
        try:
            conn = psycopg2.connect(
                host=PSQL_HOST,
                port=PSQL_PORT,
                user=PSQL_USER,
                password=PSQL_PASS,
                dbname=PSQL_DB
            )
            conn.autocommit = True
            print("[PSQL] Connected.")
            return conn
        except Exception as e:
            print(f"[PSQL] Connection failed: {e}, retrying in 3s...")
            time.sleep(3)

conn = connect_psql()
cursor = conn.cursor()

# ---------------------------------------------------------
# MQTT Message Handler
# ---------------------------------------------------------

def on_message(client, userdata, msg):
    payload_raw = msg.payload.decode()
    print(f"[MQTT] Received on {msg.topic}: {payload_raw}")

    try:
        payload = json.loads(payload_raw)

        # REQUIRED FIELDS
        site_id = payload["site_id"]
        device_id = payload["device_id"]
        sensor_name = payload["sensor_name"]
        sensor_value = float(payload["sensor_value"])
        unit = payload.get("unit")

        # timestamp may be provided OR auto-generated
        timestamp = payload.get("timestamp")
        if timestamp:
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        else:
            timestamp = datetime.now(timezone.utc)

        # Insert into DB
        cursor.execute(
            """
            INSERT INTO sensor_data
            (site_id, device_id, timestamp, sensor_name, sensor_value, unit, raw)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                site_id,
                device_id,
                timestamp,
                sensor_name,
                sensor_value,
                unit,
                Json(payload)
            )
        )

        print(f"[DB] Inserted {sensor_name}={sensor_value} for device {device_id}")

    except Exception as e:
        print(f"[ERROR] Failed to process message: {e}")
        print(f"[ERROR] Raw payload: {payload_raw}")

# ---------------------------------------------------------
# MQTT Setup
# ---------------------------------------------------------

def create_mqtt_client():
    client = mqtt.Client()

    # TLS secure connection
    client.tls_set(
        ca_certs=MQTT_CA,
        certfile=None,
        keyfile=None,
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLS,
        ciphers=None
    )

    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_message = on_message

    return client

mqtt_client = create_mqtt_client()

# ---------------------------------------------------------
# MQTT Connection Loop
# ---------------------------------------------------------

def connect_mqtt():
    while True:
        try:
            mqtt_client.connect(MQTT_HOST, MQTT_PORT)
            print(f"[MQTT] Connected to {MQTT_HOST}:{MQTT_PORT}")
            return
        except Exception as e:
            print(f"[MQTT] Connection failed: {e}, retrying in 3s...")
            time.sleep(3)

connect_mqtt()

# Subscribe to topics
for topic in MQTT_TOPICS:
    mqtt_client.subscribe(topic)
    print(f"[MQTT] Subscribed to: {topic}")

print("[MQTT] Listening for messages...")
mqtt_client.loop_forever()
