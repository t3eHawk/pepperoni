"""Various system information, parameters and arguments."""

import argparse
import ast
import datetime as dt
import json
import os
import pip
import platform
import socket
import sys


# Path to user JSON file with parameters.
userprms = os.path.abspath(os.path.expanduser('~/.pepperoni/pepperoni.json'))


class Dataset(dict):
    """Parent class for sysinfo dataset objects.

    Dataset represents information from different system sources e.g. system
    specifications, execution arguments, user parameters or environment
    variables.
    """

    def __getattr__(self, name):
        """Implement point access to the item values.

        Parameters
        ----------
        name : str
            The argument is used to get item value by name.

        Returns
        -------
        value : any
            The value of item.
        """
        return self.get(name)

    def __repr__(self):
        """Get default (empty) dataset string representation."""
        return 'Namespace()'

    __repr__ = __repr__


class Descriptors():
    """Class represents special dataset with system descriptors.

    Such kind of parameters aimed to describe system or session specifications.
    List of available descriptors by now:

    +------------+--------------------------------------------------+
    |    Name    |                 Description                      |
    +============+==================================================+
    |hostname    |Name of the host on which scipt is running        |
    +------------+--------------------------------------------------+
    |ip          |IP address of the host on which script is running |
    +------------+--------------------------------------------------+
    |user        |Name of user who is running the script            |
    +------------+--------------------------------------------------+
    |pid         |OS PID which covers the script execution          |
    +------------+--------------------------------------------------+
    |system      |Name of the OS                                    |
    +------------+--------------------------------------------------+
    |python      |Version of used Python                            |
    +------------+--------------------------------------------------+
    |compiler    |Information of used compiler                      |
    +------------+--------------------------------------------------+
    |interpreter |Path to used Python interpreter                   |
    +------------+--------------------------------------------------+
    |script      |Path to script file that is executing             |
    +------------+--------------------------------------------------+
    |locdate     |Current local date as a string in ISO format      |
    +------------+--------------------------------------------------+
    |pip         |Information about PIP                             |
    +------------+--------------------------------------------------+

    Parameters
    ----------
    *args
        The variable arguments is used for parents class constructor.
    **kwargs
        The keyword arguments is used for parents class constructor.
    """

    def __repr__(self):
        """Get string with system descriptors as pairs of names and values."""
        items = []
        for key in self.keys():
            value = getattr(self, key)
            items.append(f'{key}={value}')
        items = ', '.join(items)
        return f'Descriptors({items})'

    __repr__ = __repr__

    def __getitem__(self, key):
        """Get system descriptor value by name."""
        return getattr(self, key)

    def keys(self):
        """List of descriptor names."""
        return ['hostname', 'ip', 'user', 'pid', 'system', 'python',
                'compiler', 'interpreter', 'script', 'pip']

    @property
    def hostname(self):
        """Name of the host on which scipt is running."""
        return platform.node()

    @property
    def ip(self):
        """IP address of the host on which script is running."""
        return socket.gethostbyname(socket.gethostname())

    @property
    def user(self):
        """Name of user who is running the script."""
        return os.getlogin()

    @property
    def pid(self):
        """OS PID which covers the script execution."""
        return os.getpid()

    @property
    def system(self):
        """Name of the OS."""
        return platform.platform()

    @property
    def python(self):
        """Version of used Python."""
        version = platform.python_version()
        architecture = platform.architecture()[0]
        return f'{version}-{architecture}'

    @property
    def compiler(self):
        """Information of used compiler."""
        return platform.python_compiler()

    @property
    def interpreter(self):
        """Path to used Python interpreter."""
        return sys.executable

    @property
    def script(self):
        """Path to script file that is executing."""
        return os.path.abspath(sys.argv[0])

    @property
    def pip(self):
        """Information about PIP."""
        return pip.__version__

    @property
    def locdate(self):
        """Get current local date as a string in ISO format."""
        return dt.datetime.now().isoformat(sep=' ', timespec='seconds')


class Parameters(Dataset):
    """Class represents dataset with user parameters.

    This parameters are taken from the execution arguments and from the special
    JSON file located at user's home directory.

    Parameters from execution arguments must look like paramter=value. By
    default all values passed this way will be perceived as strings but
    application will try to define correct Python data type.
    JSON file must be ~/.pypyrus/prms.json. Parameters in that file must be
    presented as a list of dictionaries with keys: name, value, description.
    Name and description types must be a string and value type can be any
    desirable JSON data type. By default values will be converted from JSON
    data type to appropriate Python data type.
    """

    def __repr__(self):
        """Get user parameters as pairs of names and values."""
        items = []
        for key, value in self.items():
            items.append(f'{key}={value}')
        items = ', '.join(items)
        return f'Parameters({items})'


class Environment(Dataset):
    """Class represents dataset with environment variables.

    Values in dataset presented as it is - as method os.environ.items()
    returns.
    """

    def __repr__(self):
        """Get string with environment variables names."""
        items = ', '.join(self.keys())
        return f'Environment({items})'


class Sysinfo():
    """Class unites all datasets in one structure.

    Also that class reflects the logic of how all datasets must be filled.
    Sysinfo include instances of Descriptors, Parameters and Environment
    classes. And it provides additional Namespace object containing flag
    arguments parsed with argparse.ArgumentParser().

    All datasets are dictionary-like that means items can be acccessed by get
    item operation e.g. Sysinfo.desc['hostname']. Also items can accessed by
    point e.g. Sysinfo.desc.hostname.
    Take into account that dataset item names are all lower cased no matter
    what was in original source.

    Attributes
    ----------
    args : argparser.Namespace
        Recognized flag arguments.
    desc : Descriptors
        Instance of Descriptors class.
    prms : Parameters
        Instance of Parameters class.
    env : Environment
        Instance of Environment class.
    anons : list or str
        Unrecognized flag and execution arguments.
    """

    def __init__(self):
        self.argparser = argparse.ArgumentParser()
        self.args = None
        self.desc = Descriptors()
        self.prms = Parameters()
        self.env = Environment()
        self.anons = []
        self.read(args=True, user=True, env=True)
        pass

    def __repr__(self):
        """Get sysinfo string representation."""
        return f'{self.args}\n{self.desc}\n{self.prms}\n{self.env}'

    def read(self, args=True, user=False, env=False):
        """Read all datasets.

        Parameters
        ----------
        args : bool
            The argument is used to read execution arguments. Default is True.
        user : bool
            The argument is used to read user parameters. Default is False
        env : bool
            The argument is used to read environment variables. Default is
            False.
        """
        if args is True:
            # Parse all arguments from execution.
            knowns, unknowns = self.argparser.parse_known_args()
            # All known arguments on this read become Sysyinfo.args.
            self.args = knowns
            # Clear anons because between previous and current read unknown
            # argumnts could be added to parser.
            self.anons.clear()
            # If value can not be parsed then it puts to Sysinfo.anons.
            # In other case it puts to Sysinfo.prms.
            for item in unknowns:
                try:
                    key, value = item.split('=')
                except ValueError:
                    self.anons.append(item)
                else:
                    key = key.lower()
                    value = self._validate_value(value)
                    self.prms[key] = value
        if user is True:
            if os.path.exists(userprms) is True:
                with open(userprms, 'r') as fh:
                    for item in json.load(fh):
                        if isinstance(item, dict) is True:
                            name = item.get('name')
                            if (isinstance(name, str) is True and
                                self.prms.get(name) is None):
                                key = name.lower()
                                value = item.get('value')
                                self.prms[key] = value
        if env is True:
            for key, value in os.environ.items():
                key = key.lower()
                self.env[key] = value
        pass

    def argument(self, *args, **kwargs):
        """Shorcut for argparser.add_argument() method.

        Parameters
        ----------
        *args
            The variable arguments used for argparser.add_argument().
        **kwargs
            The keyword arguments used for argparser.add_argument().
        """
        self.argparser.add_argument(*args, **kwargs)
        self.read()
        pass

    def _validate_value(self, value):
        # Validate and convert value of string type to possible Python data
        # type. If value can be presented as int, float, bool, bytes,
        # bytearray, none, then converted value will be returned. In other
        # case initial string will be returned.
        try:
            value = ast.literal_eval(value)
            return value
        except ValueError:
            return value
