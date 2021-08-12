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
        'aws_info_logger': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    }
}
