import logging
import logging.config
import os

# Define the logger configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'detailed',
            'filename': os.path.join('logs', 'app.log'),  
            'mode': 'a',
        },
    },
    'loggers': {
        '': {  
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

def setup_logging():
    """Setup logging configuration"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logging.config.dictConfig(LOGGING_CONFIG)

setup_logging()


logger = logging.getLogger(__name__)
