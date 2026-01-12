import logging
import board
import busio
from adafruit_ads1x15.ads1x15 import Pin
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

# =============================
# CALIBRATION VALUES (IMPORTANT)
# =============================
# Measure these values once with your sensor:
#  - DRY: sensor in air
#  - WET: sensor fully submerged in water

DRY_VOLTAGE = 2.48    # example: adjust after calibration
WET_VOLTAGE = 1.0    # example: adjust after calibration

# =============================
# I2C / ADC SETUP
# =============================
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)

# Use channel A0
channel = AnalogIn(ads, Pin.A0)

# =============================
# READ FUNCTION
# =============================
def read():
    """
    Reads soil moisture via ADS1115 and returns percentage.
    0% = dry, 100% = wet
    """
    try:
        voltage = channel.voltage
        logging.info(f"Soil sensor voltage: {voltage:.3f} V")

        # Clamp voltage to calibration range
        voltage = max(min(voltage, DRY_VOLTAGE), WET_VOLTAGE)

        # Convert voltage → percentage
        percentage = (
            (DRY_VOLTAGE - voltage)
            / (DRY_VOLTAGE - WET_VOLTAGE)
        ) * 100

        percentage = round(percentage, 1)

        logging.info(f"Soil moisture: {percentage}%")
        return percentage

    except Exception as e:
        logging.error(f"Error reading soil moisture sensor: {e}")
        return None
