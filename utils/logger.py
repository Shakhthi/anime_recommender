import logging
import os
from datetime import datetime

LOGS_DIR = f"logs/{datetime.now().strftime('%m-%Y')}"
os.makedirs(LOGS_DIR,exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, f"log_{datetime.now().strftime('%m-%d-%Y')}.log")

logging.basicConfig(
    filename=LOG_FILE,
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
""" 
if __name__ == "__main__":
    logger = get_logger(__name__)
    logger.info("Logger initialized successfully.") 
    logger.info("This is a test log message.") """