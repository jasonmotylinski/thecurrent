import logging
import config

def init_logging(app):
    """Initialize Flask logging configuration"""
    
    # Set the log level based on DEBUG flag
    log_level = logging.DEBUG if config.DEBUG else logging.INFO
    
    # Configure the Flask app logger
    app.logger.setLevel(log_level)
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add the handler to the Flask app logger
    app.logger.addHandler(console_handler)
    
    # Also configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Log the startup message
    app.logger.info('Flask application startup') 