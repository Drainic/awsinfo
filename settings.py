"""Global settings
The file contains global variables, settings, pathes, etc
"""
# If there is no value for the filed this variable will be applied
NO_VALUE = None

### Logger section
LOGGER_NAME = "awsinfo_logger"
LOGGER_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'std_format': {
            'format': '{asctime} - {levelname} - {message}',
            'style': '{'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'std_format'
        }
    },
    'loggers': {
        LOGGER_NAME: {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    }
}
