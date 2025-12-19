import random
import logging

def read():
    """
    Mock reading of temperature in Celsius.
    """
    value = round(random.uniform(10.0, 30.0), 1)
    logging.info(f"[MOCK] Temperature reading: {value}")
    return value