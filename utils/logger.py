"""
Logging utility for Weather Shopper application
"""
import os
import datetime
from pathlib import Path
from loguru import logger

class LoggerSetup:
    """Logger setup class for Weather Shopper application"""
    
    @staticmethod
    def setup_logger(browser_name: str, session: bool = False) -> None:
        """Setup loguru logger with appropriate configuration
        
        Args:
            browser_name: Type of browser for which logs are being generated
            session: Whether this is a session-level logger (single log file for all tests)
        """
        # Create a timestamp for this run
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.datetime.now().strftime("%H-%M-%S")
        
        # Create the logs directory structure
        log_dir = Path("logs") / current_date / browser_name
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log filename - for sessions use a fixed name, otherwise include timestamp
        if session:
            log_file = log_dir / "test_session.log"
            # Clear the file if it exists to start fresh
            if os.path.exists(log_file):
                open(log_file, 'w').close()
        else:
            log_file = log_dir / f"{current_time}.log"
        
        # Remove default handler
        logger.remove()
        
        # Configure loguru with the new log file path
        logger.configure(handlers=[
            {
                "sink": log_file,
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                "level": "DEBUG",
                "rotation": "5 MB",
            },
            {
                "sink": lambda msg: print(msg),  # Also log to console
                "format": "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
                "level": "INFO",
            },
        ])
        
        if session:
            logger.info(f"Started new test SESSION with {browser_name} browser - all tests will use this single browser instance")
        else:
            logger.info(f"Started new test run with {browser_name} browser")
        
        return logger
