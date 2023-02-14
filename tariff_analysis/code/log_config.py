"""
Module to configure logging settings. Minimises the amount of extra
code required in the calling modules and more DRY, as readable as 
YAML and allows flexibility (e.g. by embedding some simple logic, 
like importing filenames via f-strings).

Useful sources: 
Intros:
- https://realpython.com/python-logging/#other-configuration-methods
- https://www.toptal.com/python/in-depth-python-logging 

Dict config:
- https://docs.python.org/3/library/logging.config.html#logging-config-api
- https://docs.python.org/3/howto/logging-cookbook.html#an-example-dictionary-based-configuration   
"""


#======================================================================
# Import libraries
#======================================================================
import config as c

#======================================================================
# Logging settings
#======================================================================
LOG_CONFIG = {
  'version': 1,
  'disable_existing_loggers': False,
  'formatters': {
    'simple': {
      'format': '%(levelname)s, %(name)s.%(funcName)s, %(message)s'
    },
    'verbose': {
      'format': '%(asctime)s, %(levelname)s, %(name)s.%(funcName)s:%(lineno)d, %(message)s',
      'datefmt': '%Y-%m-%d %H:%M:%S'
    }
  },
  'handlers': {
    'console': {
      'class': 'logging.StreamHandler',
      'level': 'INFO',
      'formatter': 'simple',
      'stream': 'ext://sys.stdout'
    },
    'file': {
      'class': 'logging.FileHandler',
      'level': 'DEBUG',
      'formatter': 'verbose',
      'filename': f'{c.LOG_FILE}',
      'encoding': 'utf8'
    }
  },
  'loggers':{
    '': { #root logger
      'level': 'DEBUG',
      'handlers': ['console', 'file']
    },
    'file_logger': {
      'level': 'DEBUG',
      'handlers': ['console', 'file']
    },    
    'console_logger': {
      'level': 'INFO',
      'handlers': ['console'],
    }
  }
}