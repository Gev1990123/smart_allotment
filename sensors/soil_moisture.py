import logging
import board
import busio
from adafruit_ads1x15.ads1x15 import Pin
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
from typing import Dict, Optional

# =============================
# CALIBRATION
# =============================

PROBES = {
    'bed_a': {'channel': Pin.A0, 'dry': 2.48, 'wet': 1.0},
    'bed_b': {'channel': Pin.A1, 'dry': 2.48, 'wet': 1.0}, 
    'greenhouse': {'channel': Pin.A2, 'dry': 2.48, 'wet': 1.0},
    'compost': {'channel': Pin.A3, 'dry': 2.48, 'wet': 1.0}
}

# =============================
# I2C / ADC SETUP
# =============================
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)

# Create channels for all probes

channels = {name: AnalogIn(ads, config['channel']) for name, config in PROBES.items()}

# =============================
# READ SINGLE PROBE
# =============================
def read(probe_name: str = 'bed_a') -> Optional[float]:
    """Read specific soil probe"""
    if probe_name not in PROBES:
        logging.error(f"Unknown probe: {probe_name}")
        return None
    
    try:
        channel = channels[probe_name]
        config = PROBES[probe_name]
        
        voltage = channel.voltage
        voltage = max(min(voltage, config['dry']), config['wet'])
        
        percentage = (
            (config['dry'] - voltage) / 
            (config['dry'] - config['wet'])
        ) * 100
        
        return round(percentage, 1)
        
    except Exception as e:
        logging.error(f"Error reading {probe_name}: {e}")
        return None
    
# =============================
# READ ALL PROBES (NEW!)
# =============================
def read_all() -> Dict[str, Optional[float]]:
    """Read all soil probes at once"""
    results = {}
    for probe_name in PROBES.keys():
        results[probe_name] = read(probe_name)
    return results

# =============================
# BACKWARD COMPATIBLE
# =============================
#def read():  # Keep old single-probe API
#    """Backward compatible - reads bed_a"""
#    return read('bed_a')
