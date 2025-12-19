import random
import logging

def read():
    """
    Mock reading of soil moisture for testing.
    Returns an integer from 0 (dry) to 100 (wet).
    """
    value = random.randint(0, 100)
    logging.info(f"[MOCK] Soil moisture reading: {value}")
    return value