# utils/logger.py - COMPLETE VERSION
import logging
import logging.config
import os
from typing import Dict, Any

def get_project_logs_dir() -> str:
    """Find project root and ensure logs/ exists"""
    current_dir = os.path.abspath(os.path.dirname(__file__))
    while os.path.basename(current_dir) != 'smart_allotment':
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            raise RuntimeError("Could not find smart_allotment project root")
        current_dir = parent
    
    log_dir = os.path.join(current_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "app": {
            "format": "%(asctime)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        # APP: file + console
        "app_file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",  # Captures INFO, WARNING, ERROR, DEBUG
            "formatter": "app",
            "filename": lambda: os.path.join(get_project_logs_dir(), "app.log"),
            "mode": "a",
        },
        "app_console": {
            "class": "logging.StreamHandler",
            "level": "INFO",  # Console shows INFO+
            "formatter": "app",
        },
        # SENSORS: file only (detailed)
        "sensors_file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",  # All levels
            "formatter": "detailed",
            "filename": lambda: os.path.join(get_project_logs_dir(), "sensors.log"),
            "mode": "a",
        },
        # NOTIFICATIONS: file only  
        "notifications_file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "detailed", 
            "filename": lambda: os.path.join(get_project_logs_dir(), "notifications.log"),
            "mode": "a",
        }
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["app_file", "app_console"],
            "propagate": False
        },
        "sensors": {
            "level": "DEBUG",
            "handlers": ["sensors_file"],
            "propagate": False
        },
        "notifications": {
            "level": "DEBUG",
            "handlers": ["notifications_file"], 
            "propagate": False
        }
    },
    "root": {
        "level": "WARNING",  # Root only WARNING+ 
        "handlers": ["app_file", "app_console"]
    }
}

def setup_logging():
    """Initialize ALL loggers ONCE at startup"""
    # Fix lambda filename issue for dictConfig
    for handler in LOGGING_CONFIG["handlers"].values():
        if callable(handler.get("filename")):
            handler["filename"] = handler["filename"]()
    
    logging.config.dictConfig(LOGGING_CONFIG)

def get_logger(category: str) -> logging.Logger:
    """Get pre-configured logger: 'app', 'sensors', 'notifications'"""
    return logging.getLogger(category)
