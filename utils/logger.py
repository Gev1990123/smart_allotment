# utils/logger.py
import logging
import os

def setup(log_file="data/logs/app.log"):
    """
    Sets up logging for the Smart Allotment app.

    Args:
        log_file (str): Path to the log file
    """
    # Ensure the logs directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Configure logging
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Logging initialized")