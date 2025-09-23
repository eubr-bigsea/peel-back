import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logger(log_dir='./peel-back/.logs/', logger_name=__name__, logger_level=logging.DEBUG):
    # Create a logger with the specified name
    logger = logging.getLogger(logger_name)
    logger.setLevel(logger_level)
    
    if not logger.handlers:
        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%d/%m/%Y %H:%M:%S')

        # Create a directory for logs if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Create a rotating file handler for writing log messages
        file_handler = RotatingFileHandler(os.path.join(log_dir, 'app.log'), maxBytes=10*1024*1024, backupCount=5)
        file_handler.setLevel(logger_level)
        file_handler.setFormatter(formatter)

        # Create a stream handler for displaying log messages on the console
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logger_level)
        stream_handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger

# Example usage:
# logger = setup_logger()
# logger.debug("Debug message")
# logger.info("Info message")
# logger.warning("Warning message")
# logger.error("Error message")
