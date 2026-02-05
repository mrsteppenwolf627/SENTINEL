import logging
import sys
from pythonjsonlogger import jsonlogger
from .config import settings

def setup_logging():
    """Configures structured JSON logging."""
    logger = logging.getLogger()
    
    # Check if handlers already exist to avoid duplicates
    if logger.handlers:
        return logger
        
    logHandler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel(settings.LOG_LEVEL)
    
    return logger

logger = setup_logging()
