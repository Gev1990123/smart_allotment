import time
from utils import logger, notifications
from sensors import soil_moisture, temperature, light

# Initialize logging
logger.setup()
import logging

logging.info("Starting Smart Allotment main loop with mock sensors")

LOW_MOISTURE_THRESHOLD = 30 #Percent

while True:
    sm = soil_moisture.read()
    temp = temperature.read()
    light_val = light.read()
    
    logging.info(f"Readings -> Soil: {sm}, Temp: {temp}, Light: {light_val}")

    if sm < LOW_MOISTURE_THRESHOLD:
        notifications.alert_low_moisture("Plot 1", sm)

    #time.sleep(10)  # 10 seconds between readings for testing
    time.sleep(300)  # 5 minutes between readings for testing