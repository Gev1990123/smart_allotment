import glob
import time
import logging
import os
from utils.logger import get_logger

# =============================
# Setup Logging
# =============================

logger = get_logger("sensors")

BASE_DIR = '/sys/bus/w1/devices/'
DEVICE_ID = '28-0b25516af7db'  # Your sensor ID
DEVICE_FILE = os.path.join(BASE_DIR, DEVICE_ID, 'w1_slave')

def read_temp_raw():
    """Read raw data from DS18B20 sensor."""
    with open(DEVICE_FILE, 'r') as f:
        lines = f.readlines()
    return lines

def read():
    """
    Read temperature in Celsius from DS18B20 sensor.
    """
    try:
        lines = read_temp_raw()
        if len(lines) >= 2 and lines[0].strip().endswith('YES'):
            temp_string = lines[1][lines[1].find('t=')+2:]
            if temp_string:
                temp_c = float(temp_string) / 1000.0
                logging.info(f"Temperature: {temp_c:.1f}°C")
                return round(temp_c, 1)
    except (IOError, IndexError, ValueError) as e:
        logging.error(f"Sensor read error: {e}")
        return None