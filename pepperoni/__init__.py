"""Developer-friendly Python toolkit.

Pepperoni is a toolkit for Python applications development making the process
more convenient.

Pepperoni provides a set of out-of-the-box solutions:
* Logger - alternative for Python built-in logging module with similar syntax
  but its own way of configuration and set of unique features.
* Sysinfo - container with information from different inputs such as systems
  descriptors, environment variables, execution arguments, user arguments,
  user commands, etc.
* Credentials - generic way for access to the most secure information placed
  into the special configuration files from within your applications.
* Database - wrapper of fantastic SQLAlchemy, gives simple interface that
  allow you to connect and interract with database and its objects from within
  your applications using minumum code.
"""


from .cache import all_loggers
from .credentials import Credentials
from .database import Database
from .logger import Logger
from .sysinfo import Sysinfo
from .utils import py_file

__author__ = 'Timur Faradzhov'
__copyright__ = 'Copyright 2020, The Pepperoni Project'
__credits__ = ['Timur Faradzhov']

__license__ = 'MIT'
__version__ = '0.2.1'
__maintainer__ = 'Timur Faradzhov'
__email__ = 'timurfaradzhov@gmail.com'
__status__ = 'Development'


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


__logger = logger(file=False, console=True, debug=True)


def info(*args, **kwargs):
    """Write INFO message to main application logger."""
    __logger.info(*args, **kwargs)
    pass


def debug(*args, **kwargs):
    """Write DEBUG message to main application logger."""
    __logger.debug(*args, **kwargs)
    pass


def warning(*args, **kwargs):
    """Write WARNING message to main application logger."""
    __logger.warning(*args, **kwargs)
    pass


def error(*args, **kwargs):
    """Write ERROR message to main application logger."""
    __logger.error(*args, **kwargs)
    pass


def critical(*args, **kwargs):
    """Write CRITICAL message to main application logger."""
    __logger.critical(*args, **kwargs)
    pass


def configure(*args, **kwargs):
    """Configure main application logger."""
    __logger.configure(*args, **kwargs)
    pass


def sysinfo():
    """Get Sysinfo object."""
    return Sysinfo()


def credentials():
    """Get Credentials object."""
    return Credentials()


def database(*args, **kwargs):
    """Get Database object."""
    return Database(*args, **kwargs)
