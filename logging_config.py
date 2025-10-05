"""
Logging configuration for Lethai Concierge Referral Bot
"""
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console_output: bool = True
) -> None:
    """
    Setup logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        console_output: Whether to output to console
    """
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific loggers
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    logging.getLogger('gspread').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

class BotLogger:
    """Custom logger for bot operations"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, extra=kwargs)
    
    def log_user_action(self, user_id: int, action: str, details: str = ""):
        """Log user action"""
        self.info(f"User {user_id} performed action: {action}", 
                 extra={'user_id': user_id, 'action': action, 'details': details})
    
    def log_admin_action(self, admin_id: int, action: str, target_user_id: int = None, details: str = ""):
        """Log admin action"""
        self.info(f"Admin {admin_id} performed action: {action}", 
                 extra={'admin_id': admin_id, 'action': action, 'target_user_id': target_user_id, 'details': details})
    
    def log_error(self, error: Exception, context: str = ""):
        """Log error with context"""
        self.error(f"Error in {context}: {str(error)}", 
                  extra={'error': str(error), 'context': context, 'exception': type(error).__name__})
    
    def log_system_event(self, event: str, details: str = ""):
        """Log system event"""
        self.info(f"System event: {event}", 
                 extra={'event': event, 'details': details})

# Initialize logging on import
if __name__ != "__main__":
    # Setup logging from environment variables
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', 'logs/bot.log')
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    
    if debug_mode:
        log_level = 'DEBUG'
    
    setup_logging(
        level=log_level,
        log_file=log_file,
        console_output=True
    )



