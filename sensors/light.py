import logging
import board
import busio
import adafruit_bh1750
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
PROBES_CONFIG: Dict[str, Dict] = {}
SENSORS: Dict[str, adafruit_bh1750.BH1750] = {}

_i2c = busio.I2C(board.SCL, board.SDA)

# =============================
# DYNAMIC PROBES FROM DATABASE
# =============================
def get_active_light_probes() -> Dict[str, Dict]:
    """
    Get ONLY active light probes from database.
    Uses Probe.channel as I2C address (e.g. 'I2C-0x23').
    """
    with current_app.app_context():
        probes = Probe.query.filter_by(active=True, sensor_type='light').all()
        probe_config: Dict[str, Dict] = {}

        for probe in probes:
            try:
                # Expect channel like "I2C-0x23" or "I2C-35"
                if not probe.channel.startswith("I2C-"):
                    raise ValueError(
                        f"Invalid light channel format '{probe.channel}' "
                        f"for probe {probe.name}. Expected 'I2C-0x23' etc."
                    )
                addr_str = probe.channel[4:]
                if addr_str.startswith("0x"):
                    address = int(addr_str, 16)
                else:
                    address = int(addr_str)

                probe_config[probe.name] = {
                    'address': address,
                    'min_threshold': probe.min_value if probe.min_value is not None else 0.0,
                    'max_threshold': probe.max_value if probe.max_value is not None else 65535.0,
                    'description': probe.description or '',
                }
                logging.info(
                    f"Loaded light probe: {probe.name} (addr=0x{address:02X})"
                )
            except Exception as e:
                logging.error(f"Invalid config for light probe {probe.name}: {e}")

        return probe_config


# =============================
# DYNAMIC PROBES FROM DATABASE
# =============================
def get_active_light_probes() -> Dict[str, Dict]:
    """
    Get ONLY active light probes from database.
    Uses Probe.channel as I2C address (e.g. 'I2C-0x23').
    """
    with current_app.app_context():
        probes = Probe.query.filter_by(active=True, sensor_type='light').all()
        probe_config: Dict[str, Dict] = {}

        for probe in probes:
            try:
                # Expect channel like "I2C-0x23" or "I2C-35"
                if not probe.channel.startswith("I2C-"):
                    raise ValueError(
                        f"Invalid light channel format '{probe.channel}' "
                        f"for probe {probe.name}. Expected 'I2C-0x23' etc."
                    )
                addr_str = probe.channel[4:]
                if addr_str.startswith("0x"):
                    address = int(addr_str, 16)
                else:
                    address = int(addr_str)

                probe_config[probe.name] = {
                    'address': address,
                    'min_threshold': probe.min_value if probe.min_value is not None else 0.0,
                    'max_threshold': probe.max_value if probe.max_value is not None else 65535.0,
                    'description': probe.description or '',
                }
                logging.info(
                    f"Loaded light probe: {probe.name} (addr=0x{address:02X})"
                )
            except Exception as e:
                logging.error(f"Invalid config for light probe {probe.name}: {e}")

        return probe_config


# =============================
# CREATE DYNAMIC SENSORS
# =============================
def light_init_channels():
    """
    Initialize BH1750 sensors for all active light probes.
    Call AFTER app context exists (same as soil_moisture.init_channels()).
    """
    global PROBES_CONFIG, SENSORS
    PROBES_CONFIG = get_active_light_probes()

    SENSORS.clear()
    for name, config in PROBES_CONFIG.items():
        try:
            sensor = adafruit_bh1750.BH1750(_i2c, address=config['address'])
            SENSORS[name] = sensor
            logging.info(f"Initialized BH1750 for light probe {name}")
        except Exception as e:
            logging.error(f"Failed to init BH1750 for {name}: {e}")

# =============================
# READ SINGLE LIGHT PROBE
# =============================
def read(probe_name: str = None) -> Optional[float]:
    """
    Read specific light probe from database config.
    If probe_name is None, read the first active light probe.
    Returns lux (float) or None.
    """
    probes = get_active_light_probes()
    if not probes:
        logging.error("No active light probes found")
        return None

    # Default to first configured light probe if not specified
    if probe_name is None:
        probe_name = next(iter(probes.keys()))

    if probe_name not in probes:
        logging.error(f"Unknown light probe: {probe_name}")
        return None

    try:
        sensor = SENSORS.get(probe_name)
        if not sensor:
            logging.warning(f"No BH1750 initialized for {probe_name}")
            return None

        config = probes[probe_name]

        # BH1750 .lux gives ambient light in lux directly.[web:2][web:11]
        lux = sensor.lux
        result = round(lux, 1)

        # Optional threshold logging
        if result < config['min_threshold']:
            logging.warning(
                f"{probe_name}: {result} lux below min {config['min_threshold']}"
            )
        if result > config['max_threshold']:
            logging.warning(
                f"{probe_name}: {result} lux above max {config['max_threshold']}"
            )

        logging.info(
            f"{probe_name}: {result} lux "
            f"(addr=0x{config['address']:02X})"
        )
        return result

    except Exception as e:
        logging.error(f"Error reading light probe {probe_name}: {e}")
        return None
    

# =============================
# READ ALL ACTIVE LIGHT PROBES
# =============================
def read_all() -> Dict[str, Optional[float]]:
    """
    Read all ACTIVE light probes from database.
    Returns {probe_name: lux or None}.
    """
    results: Dict[str, Optional[float]] = {}
    light_probes = get_active_light_probes()

    for probe_name in light_probes.keys():
        results[probe_name] = read(probe_name)

    logging.info(f"Read all light probes: {results}")
    return results