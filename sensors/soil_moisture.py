import logging
import board
import busio
from adafruit_ads1x15.ads1x15 import Pin
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
from typing import Dict, Optional
from flask import current_app
from models.probes import Probe
from utils.logger import setup

# =============================
# Setup Logging
# =============================

setup("sensor.log")

# =============================
# GLOBAL STATE
# =============================
PROBES_CONFIG = {}
CHANNELS = {}
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)

# =============================
# DYNAMIC PROBES FROM DATABASE
# =============================

def get_active_soil_probes() -> Dict[str, Dict]:
    """Get ONLY active soil probes from database"""
    with current_app.app_context():  # SAFE - only called AFTER app context exists
        probes = Probe.query.filter_by(active=True, sensor_type='soil').all()
        probe_config = {}
        
        for probe in probes:
            try:
                channel_pin = getattr(Pin, probe.channel)
                probe_config[probe.name] = {
                    'channel': channel_pin,
                    'dry': probe.dry_voltage or 2.48,
                    'wet': probe.wet_voltage or 1.0,
                    'min_threshold': probe.min_value or 20,
                    'max_threshold': probe.max_value or 90,
                    'description': probe.description or ''
                }
                logging.info(f"Loaded soil probe: {probe.name} ({probe.channel})")
            except AttributeError:
                logging.error(f"Invalid channel '{probe.channel}' for probe {probe.name}")
        
        return probe_config

# =============================
# CREATE DYNAMIC CHANNELS
# =============================
def soil_init_channels():
    """Initialize AFTER app context exists"""
    global PROBES_CONFIG, CHANNELS
    PROBES_CONFIG = get_active_soil_probes()
    
    CHANNELS.clear()
    for name, config in PROBES_CONFIG.items():
        CHANNELS[name] = AnalogIn(ads, config['channel'])
        logging.info(f"Initialized channel for {name}")

# =============================
# READ SINGLE PROBE
# =============================
def read(probe_name: str) -> Optional[float]:
    """Read specific soil probe from database config"""
    probes = get_active_soil_probes()
    if probe_name not in probes:
        logging.error(f"Unknown soil probe: {probe_name}")
        return None
    
    try:
        channel = CHANNELS.get(probe_name)
        if not channel:
            logging.warning(f"No channel initialized for {probe_name}")
            return None
        
        config = probes[probe_name]
        voltage = channel.voltage
        
        # Clamp voltage to calibration range
        voltage = max(min(voltage, config['dry']), config['wet'])

        # Convert to percentage (soil moisture)
        percentage = (
            (config['dry'] - voltage) / 
            (config['dry'] - config['wet'])
        ) * 100
        
        result = round(percentage, 1)
        logging.info(f"{probe_name}: {result}% (V={voltage:.3f}, dry={config['dry']}, wet={config['wet']})")
        return result
        
    except Exception as e:
        logging.error(f"Error reading {probe_name}: {e}")
        return None
    
# =============================
# READ ALL ACTIVE SOIL PROBES
# =============================
def read_all() -> Dict[str, Optional[float]]:
    """Read all ACTIVE SOIL probes from database"""
    results = {}
    soil_probes = get_active_soil_probes()
    
    for probe_name in soil_probes.keys():
        results[probe_name] = read(probe_name)
    
    logging.info(f"Read all soil probes: {results}")
    return results