import logging
import os

def setup(log_file="app.log"):
    """
    Sets up logging for the Smart Allotment app.
    Logs to both file and console.
    """

    # Calculate project root
    current_dir = os.path.abspath(os.path.dirname(__file__))
    while os.path.basename(current_dir) != 'smart_allotment':
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            raise RuntimeError("Could not find smart_allotment project root")
        current_dir = parent

    PROJECT_ROOT = current_dir
    LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
    os.makedirs(LOG_DIR, exist_ok=True)

    if not os.path.isabs(log_file):
        log_file = os.path.join(LOG_DIR, log_file)
    
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

    # Werkzeug Logging
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)
    werkzeug_logger.handlers = [logging.StreamHandler()]