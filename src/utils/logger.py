# Logging utilities 

import logging
import sys
from pathlib import Path

def setup_logger(name):
    """
    Set up a logger with consistent formatting and file output.
    
    Args:
        name (str): The name of the logger (typically __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(log_dir / "aura.log")
    
    # Create formatters and add it to handlers
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)
    
    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger 
