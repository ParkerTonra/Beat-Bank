# src/logging_config.py
import logging
import os

LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'app.log')

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE_PATH),
            logging.StreamHandler()
        ]
    )