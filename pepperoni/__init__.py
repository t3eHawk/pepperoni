from .conf import all_loggers
from .formatter import Formatter
from .header import Header
from .logger import Logger
from .output import Output
from .record import Record
from .utils import py_file

__author__ = 'Timur Faradzhov'
__copyright__ = 'Copyright 2019, The Pepperoni Project'
__credits__ = ['Timur Faradzhov']

__license__ = 'MIT'
__version__ = '0.1.0'
__maintainer__ = 'Timur Faradzhov'
__email__ = 'timurfaradzhov@gmail.com'
__status__ = 'Development'

__doc__ = 'Module for extended logging in Python.'

def logger(name=None, **kwargs):
    """Get new logger or return existing one.
    If parameter name is omitted then return main application logger.
    All other named parameters will be used for configuration.

    Parameters
    ----------
    name : str
        The name of the logger that must be created or returned.
    **kwargs
        The keyword arguments that used for logger configuration.

    Returns
    -------
    logger
        The `Logger` object.
    """
    name = name or py_file
    if all_loggers.get(name) is not None:
        if len(kwargs) > 0:
            all_loggers[name].configure(**kwargs)
        return all_loggers[name]
    else:
        return Logger(name=name, **kwargs)

getlogger = logger

applogger = getlogger(file=False, console=True, debug=True)

def info(*args, **kwargs):
    """Print INFO message in main application logger."""
    applogger.info(*args, **kwargs)
    pass

def debug(*args, **kwargs):
    """Print DEBUG message in main application logger."""
    applogger.debug(*args, **kwargs)
    pass

def warning(*args, **kwargs):
    """Print WARNING message in main application logger."""
    applogger.warning(*args, **kwargs)
    pass

def error(*args, **kwargs):
    """Print ERROR message in main application logger."""
    applogger.error(*args, **kwargs)
    pass

def critical(*args, **kwargs):
    """Print CRITICAL message in main application logger."""
    applogger.critical(*args, **kwargs)
    pass

def configure(*args, **kwargs):
    """Configure main application logger."""
    applogger.configure(*args, **kwargs)
    pass
