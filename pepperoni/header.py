"""Logging header."""

from .sysinfo import Descriptors


class Header():
    """Represents header with the most significatn application information.

    A header can be used to record the most significant variables at the start
    of logging.

    To exclude variables from header just put their names into args. The same
    can be done with a help of Header.exclude() method.
    To include variables to header just put them as items into kwargs. The same
    can be done with a help of Header.include() method. Note then variables
    can be presented both as functions returning some sting and as a regular
    string.

    Parameters
    ----------
    logger : Logger
        The argument used to set `logger` attribute.
    *args
        The variable arguments used to exclude variables from header by the
        name.
    **kwargs
        The keyword arguments used to include variables to header.

    Attributes
    ----------
    logger : Logger
        The `Logger` object that owns and uses that header.
    used : bool
        Flag to define whether header was used or not.
    length : int
        Maximum length of the header line.
    div : str
        Symbolic block used for borders.
    items : dict
        Dictionary with header variables.
    """

    def __init__(self, logger, *args, **kwargs):
        desc = Descriptors()

        self.logger = logger
        self._used = False
        self.length = logger.formatter.length
        self.div = logger.formatter.div
        self.items = {'application': lambda: self.logger.app,
                      'description': lambda: self.logger.desc,
                      'version': lambda: self.logger.version,
                      'hostname': lambda: desc.hostname,
                      'ip': lambda: desc.ip,
                      'user': lambda: desc.user,
                      'pid': lambda: desc.pid,
                      'system': lambda: desc.system,
                      'python': lambda: desc.python,
                      'compiler': lambda: desc.compiler,
                      'interpreter': lambda: desc.interpreter,
                      'script': lambda: desc.script,
                      'pip': lambda: desc.pip,
                      'locdate': lambda: desc.locdate}
        if args or kwargs:
            self.include(**kwargs)
            self.exclude(*args)
        pass

    @property
    def used(self):
        """Flag to define whether header was used or not."""
        return self._used

    def create(self):
        """Create header.

        Generate a formatted text with the list of the keys and values based on
        variables stored in `items` attribute.

        Returns
        -------
        header : str
            The header as a string.
        """
        # Change flag to determine that header is already used in logger.
        self._used = True
        # Calculate all necessary lengths.
        ln_out, ln_in, ln_name, ln_value = self._calculate_lengths()
        lines = []

        # Format of the one line of header.
        frame_format = '{div}{content:{filler}<{ln_in}}{div}\n'
        all = dict(div=self.div, ln_in=ln_in)

        # Get basic top two lines of the header.
        top = frame_format.format(content='', filler=self.div, **all)
        top += frame_format.format(content='', filler='', **all)
        lines.append(top)

        # Get all lines with the variables.
        content_format = '{name:>{ln_name}}: {value}'
        for d_name, d_value in self.items.items():
            name = d_name.upper()
            value = d_value() if callable(d_value) is True else d_value
            content = content_format.format(name=name, ln_name=ln_name,
                                            value=value)
            frame = frame_format.format(content=content, filler='', **all)
            lines.append(frame)

        # Get buttom two lines of the header.
        bottom = frame_format.format(content='', filler='', **all)
        bottom += frame_format.format(content='', filler=self.div, **all)
        lines.append(bottom)

        header = ''.join(lines)
        return header

    def include(self, pos='start', **kwargs):
        """Add variables to the header.

        Parameters
        ----------
        pos : str, optional
            The argument used for position to which new variables will be
            added.
            Can be `start` or `end`.
        **kwargs
            The keyword arguments used to include variables to header.
        """
        if pos == 'start':
            self.items = {**kwargs, **self.items}
        elif pos == 'end':
            self.items = {**self.items, **kwargs}
        pass

    def exclude(self, *args):
        """Delete some variables from the header.

        Parameters
        ----------
        *args
            The variable arguments used to exclude variables from header by the
            name.
        """
        for arg in args:
            del self.items[arg]
        pass

    def _calculate_lengths(self):
        """Calculate all lengths used in header formatting.

        Returns
        -------
        ln_out : int
            Basic lengh of header line.
        ln_in : int
            Length of text inside the line (withour borders).
        ln_name : int
            Length of the name of variable.
        ln_value : int
            Length of the value of variable.
        """
        ln_out = self.length
        ln_in = ln_out - 2
        ln_name = max([len(key) for key in self.items.keys()]) + 2
        ln_value = ln_in - ln_name
        return (ln_out, ln_in, ln_name, ln_value)
