"""
Logger Module - Centralized logging for the bot
"""
import logging
import os
from logging.handlers import RotatingFileHandler

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')
LOG_MAX_SIZE = 10485760  # 10 MB
LOG_BACKUP_COUNT = 5

class BotLogger:
    """Centralized logging for the bot"""
    
    _loggers = {}
    
    @staticmethod
    def get_logger(name):
        """
        Get or create a logger with the specified name
        
        Args:
            name: Logger name (typically module name)
            
        Returns:
            logging.Logger: Configured logger instance
        """
        if name in BotLogger._loggers:
            return BotLogger._loggers[name]
        
        logger = logging.getLogger(name)
        
        # Set log level
        log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # File handler with rotation (logs only to file, not console)
        try:
            file_handler = RotatingFileHandler(
                LOG_FILE,
                maxBytes=LOG_MAX_SIZE,
                backupCount=LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except (IOError, OSError) as e:
            logger.warning(f"Could not add file handler: {e}")
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        BotLogger._loggers[name] = logger
        return logger
    
    @staticmethod
    def log_command(user, command, args=""):
        """Log command execution"""
        logger = BotLogger.get_logger("commands")
        logger.info(f"User {user} executed: !{command} {args}")
    
    @staticmethod
    def log_error(component, error):
        """Log error occurrence"""
        logger = BotLogger.get_logger("errors")
        logger.error(f"Error in {component}: {error}")
    
    @staticmethod
    def log_api_call(service, status, response_time=None):
        """Log API call results"""
        logger = BotLogger.get_logger("api")
        msg = f"API call to {service}: {status}"
        if response_time:
            msg += f" ({response_time:.2f}s)"
        logger.info(msg)
