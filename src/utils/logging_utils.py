"""
Logging utility functions
"""
import logging
from config import LOG_FILE

def setup_logging(log_name="FinancialQA"):
    """
    Configure logging for the application
    
    Args:
        log_name: Name for the logger
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(log_name)
    
    # Configure logger if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create formatters
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create file handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger