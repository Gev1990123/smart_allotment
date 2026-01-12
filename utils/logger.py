import logging
import os

def setup(log_file="logs/app.log"):
    """
    Sets up logging for the Smart Allotment app.
    Logs to both file and console.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(file_formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logging.info("Logging initialized")