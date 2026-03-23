import os
import logging

LOG_PATH = os.getenv("APP_LOG_PATH", "app_runtime.log")

logger = logging.getLogger("multiomics_app")
logger.setLevel(logging.INFO)

if not logger.handlers:
    fh = logging.FileHandler(LOG_PATH)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

def log(msg: str):
    logger.info(msg)

