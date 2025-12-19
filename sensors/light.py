import random
import logging

def read():
    """
    Mock reading of light level (0 = dark, 100 = very bright)
    """
    value = random.randint(0, 100)
    logging.info(f"[MOCK] Light reading: {value}")
    return value