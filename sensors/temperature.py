import glob
import time
import os
from typing import Dict, Optional
from flask import current_app
from models.probes import Probe
from utils.logger import get_logger

# =============================
# Setup Logging
# =============================

logger = get_logger("sensors")

# =============================
# GLOBAL STATE
# =============================
PROBES_CONFIG: Dict[str, Dict] = {}
SENSORS: Dict[str, str] = {}  # {probe_name: device_file_path}

BASE_DIR = '/sys/bus/w1/devices/'

# =============================
# DYNAMIC PROBES FROM DATABASE
# =============================
def get_active_temp_probes() -> Dict[str, Dict]:
    """
    Get ONLY active temperature probes from database.
    Uses Probe.channel as DS18B20 device ID (e.g. '28-0b25516af7db').
    """
    with current_app.app_context():
        probes = Probe.query.filter_by(active=True, sensor_type='temperature').all()
        probe_config: Dict[str, Dict] = {}

        for probe in probes:
            try:
                # Expect channel like DS18B20 ID: "28-0b25516af7db"
                device_path = os.path.join(BASE_DIR, probe.channel, 'w1_slave')
                
                # Verify device exists
                if not os.path.exists(device_path):
                    logger.warning(f"DS18B20 device not found: {device_path}")
                    continue

                probe_config[probe.name] = {
                    'device_file': device_path,
                    'min_threshold': probe.min_value if probe.min_value is not None else -10.0,
                    'max_threshold': probe.max_value if probe.max_value is not None else 50.0,
                    'description': probe.description or '',
                }
                logger.info(f"Loaded temp probe: {probe.name} (ID={probe.channel})")
            except Exception as e:
                logger.error(f"Invalid config for temp probe {probe.name}: {e}")

        return probe_config
    

# =============================
# CREATE DYNAMIC SENSORS
# =============================
def temp_init_channels():
    """
    Initialize DS18B20 sensors for all active temperature probes.
    Just caches device file paths (no hardware init needed).
    """
    global PROBES_CONFIG, SENSORS
    PROBES_CONFIG = get_active_temp_probes()
    
    SENSORS.clear()
    for name, config in PROBES_CONFIG.items():
        SENSORS[name] = config['device_file']
        logger.info(f"Initialized DS18B20 for temp probe {name}")
    
    logger.info(f"Found {len(SENSORS)} temperature probes ready")

# =============================
# READ SINGLE TEMP PROBE
# =============================
def read(probe_name: str = None) -> Optional[float]:
    """
    Read specific temperature probe from database config.
    If probe_name is None, read first active probe.
    """
    probes = get_active_temp_probes()
    if not probes:
        logger.error("No active temperature probes found")
        return None

    # Default to first probe
    if probe_name is None:
        probe_name = next(iter(probes.keys()))

    if probe_name not in probes:
        logger.error(f"Unknown temp probe: {probe_name}")
        return None

    try:
        device_file = SENSORS.get(probe_name)
        if not device_file or not os.path.exists(device_file):
            logger.warning(f"DS18B20 device file missing for {probe_name}")
            return None

        time.sleep(0.8) # DS18B20 needs settle time - trigger conversion

        # Read raw DS18B20 data
        with open(device_file, 'r') as f:
            lines = f.readlines()
        
        if len(lines) >= 2 and lines[0].strip().endswith('YES'):
            temp_string = lines[1][lines[1].find('t=')+2:]
            if temp_string:
                temp_c = float(temp_string) / 1000.0
                result = round(temp_c, 1)
                
                config = probes[probe_name]
                # Threshold warnings
                if result < config['min_threshold']:
                    logger.warning(f"{probe_name}: {result}°C below min {config['min_threshold']}")
                if result > config['max_threshold']:
                    logger.warning(f"{probe_name}: {result}°C above max {config['max_threshold']}")
                
                logger.info(f"{probe_name}: {result}°C")
                return result
        else:
            logger.warning(f"DS18B20 CRC check failed for {probe_name}")
            return None
            
    except Exception as e:
        logger.error(f"Error reading temp probe {probe_name}: {e}")
        return None


# =============================
# READ ALL ACTIVE TEMP PROBES
# =============================
def read_all() -> Dict[str, Optional[float]]:
    """Read all ACTIVE temperature probes from database."""
    results: Dict[str, Optional[float]] = {}
    temp_probes = get_active_temp_probes()

    for probe_name in temp_probes.keys():
        results[probe_name] = read(probe_name)

    logger.info(f"Read all temp probes: {results}")
    return results

# =============================
# Rescan for sensors. 
# =============================

def refresh_channels():
    """Re-scan DB and refresh active sensors."""
    global PROBES_CONFIG, SENSORS
    logger.info("🔄 Refreshing temperature probes from DB...")
    temp_init_channels()  # Re-runs full init
    logger.info(f"Refreshed: {len(SENSORS)} active temperature probes")