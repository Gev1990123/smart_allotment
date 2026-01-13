import logging
import board
import busio
import adafruit_bh1750

# =============================
# I2C / ADC SETUP
# =============================
i2c = busio.I2C(board.SCL, board.SDA)

# Create sensor instance
sensor = adafruit_bh1750.BH1750(i2c)

# =============================
# READ FUNCTION
# =============================
def read():
    """
    Reads ambient light level.
    Returns lux (float).
    """
    try:
        lux = sensor.lux
        lux = round(lux, 1)
        #logging.info(f"Ambient light: {lux} lux")

        return lux

    except Exception as e:
        #logging.error(f"Error reading BH1750: {e}")
        return None
