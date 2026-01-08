import random
import logging
import RPi.GPIO as GPIO

SENSOR_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

#def read():
#    """
#    Mock reading of soil moisture for testing.
#    Returns an integer from 0 (dry) to 100 (wet).
#    """
#    value = random.randint(0, 100)
#    logging.info(f"[MOCK] Soil moisture reading: {value}")
#    return value

# Can be used with live data with
def read():
    """
    Reads the soil moisture sensor and returns a percentage.
    0% = completely dry, 100% = wet
    """
    try:
        value = GPIO.input(SENSOR_PIN)
        logging.info(f"GPIO Value = {value}")
        # Digital sensor: 1 = wet, 0 = dry
        percentage = 100 if value else 0
        logging.info(f"[GPIO] Soil moisture reading: {percentage}%")
        return percentage
    except Exception as e:
        logging.error(f"Error reading soil moisture: {e}")
        return None

def cleanup():
    """Clean up GPIO (call at program exit)"""
    GPIO.cleanup()