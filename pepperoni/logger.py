"""Logging tools."""

import atexit
import datetime as dt
import os
import sys
import traceback

from .cache import all_loggers
from .formatter import Formatter
from .header import Header
from .output import Root
from .record import Record


class Logger():
    """Represents a particular logger object.

    This class allows to perform advanced logging to different outputs:
    console, file, email, database table, HTML document - using information
    from different inputs: user messages, traceback, frames, user parameters
    and system descriptors.

    Each logger must have an unique name which will help to identify it.
    Main application logger will have the same name as a main python script
    file.

    Parameters
    ----------
    name : str, optional
        The argument is used te define `name` attribute
    app : str, optional
        The argument is used to set the `app` attribute.
    desc : str, optional
        The argument is used to set the `desc` attribute.
    version : str, optional
        The argument is used to set the `version` attribute.
    status : bool, optional
        The argument is used to open or close output `root`.
    console : bool, optional
        The argument is used to open or close output `console`.
    file : bool, optional
        The argument is used to open or close output `file`.
    email : bool, optional
        The argument is used to open or close output `email`.
    html : bool, optional
        The argument is used to open or close output `html`.
    table : bool, optional
        The argument is used to open or close output `table`.
    directory : str, optional
        The argument is used to set logging file folder.
    filename : str, optional
        The argument is used to set logging file name.
    extension : str, optional
        The argument is used to set logging file extension.
    smtp : dict, optional
        The argument is used to configure SMTP connection.
    db : dict, optional
        The argument is used to configure DB connection.
    format : str, optional
        The argument is used to set record template.
    info : bool, optional
        The argument is used to filter info records. The default is True.
    debug : bool, optional
        The argument is used to filter debug records. The default is False.
    warning : bool, optional
        The argument is used to filter warning records. The default is True.
    error : bool, optional
        The argument is used to filter error records. The default is True.
    critical : bool, optional
        The argument is used to filter critical records. The default is True.
    alarming : bool, optional
        The argument is used to enable or disable alarming mechanism. The
        default is True.
    control : bool, optional
        The argument is used to enable or disable execution break in case
        on error. The default is True.
    maxsize : int or bool, optional
        The argument is used to define maximum size of output file. Must be
        presented as number of bytes. The default is 10 Mb.
    maxdays : int or bool, optional
        The argument is used to define maximum number of days that will be
        logged to same file. The default is 1 which means that new output file
        will be opened at each 00:00:00.
    maxlevel : int or bool, optional
        The argument is used to define the break error level (WARNING = 0,
        ERRROR = 1, CRITICAL = 2). All that higher the break level will
        interrupt application execution. The default is 1.
    maxerrors : int or bool, optional
        The argument is used to define maximun number of errors. The default
        is False which means it is disabled.

    Attributes
    ----------
    name : str
        Name of the logger.
    app : str
        Name of the application that we are logging.
    desc : str
        Description of the application that we are logging.
    version : str
        Version of the application that we are logging.
    start_date : datetime.datetime
        Date when logging was started.
    rectypes : dict
        All available record types. Keys are used in `Logger` write methods as
        `rectype` argument. Values are used in formatting. So if you wish to
        modify `rectype` form then edit appropriate one here. If you wish to
        use own record types then just add it to that dictinary. By default we
        provide the next few record types:

        +---------+---------+
        |   Key   |  Value  |
        +=========+=========+
        |none     |NONE     |
        +---------+---------+
        |info     |INFO     |
        +---------+---------+
        |debug    |DEBUG    |
        +---------+---------+
        |warning  |WARNING  |
        +---------+---------+
        |error    |ERROR    |
        +---------+---------+
        |critical |CRITICAL |
        +---------+---------+

    messages : dict
        Messages that are printed with some `Logger` methods like `ok()`,
        `success()`, `fail()`. If you wish to modify the text of this messages
        just edit the value of appropriate item.
    with_errors : int
        The flag shows that logger catched errors in the application during its
        execution.
    count_errors : int
        Number of errors that logger catched in the application during its
        execution.
    filters : dict
        Record types filters. To filter record type just set corresponding
        item value to False.
    root : pepperoni.output.Root
        The output `Root` object.
    console : pepperoni.output.Console
        The output `Console` object. Shortcut for `Logger.root.console`.
    file : pepperoni.output.File
        The output file. Shortcut for `Logger.output.file`.
    formatter : pepperoni.formatter.Formatter
        Logger formatter which sets all formatting configuration like
        record template, error message and traceback templates, line length
        etc.
    header : pepperoni.header.Header
        The header that can be printed to the writable output.
    """

    def __init__(self, name=None, app=None, desc=None, version=None,
                 status=True, console=True, file=True, email=False, html=False,
                 table=False, directory=None, filename=None, extension=None,
                 smtp=None, db=None, format=None, info=True, debug=False,
                 warning=True, error=True, critical=True, alarming=True,
                 control=True, maxsize=(1024*1024*10), maxdays=1, maxlevel=2,
                 maxerrors=False):
        # Unique name of the logger.
        self._name = name
        # Add creating logger to special all_loggers dictinary.
        all_loggers[self._name] = self

        # Attributes describing the application.
        self.app = None
        self.desc = None
        self.version = None

        # Some logger important attributes
        self.start_date = dt.datetime.now()
        self.rectypes = {'none': 'NONE',
                         'info': 'INFO',
                         'debug': 'DEBUG',
                         'warning': 'WARNING',
                         'error': 'ERROR',
                         'critical': 'CRITICAL'}
        self.messages = {'ok': 'OK',
                         'success': 'SUCCESS',
                         'fail': 'FAIL'}

        self._with_error = False
        self._count_errors = 0
        self._all_errors = []

        # Complete the initial configuration.
        self.configure(app=app, desc=desc, version=version, status=status,
                       console=console, file=file, email=email, html=html,
                       table=table, directory=directory, filename=filename,
                       extension=extension, smtp=smtp, db=db, format=format,
                       info=info, debug=debug, warning=warning, error=error,
                       critical=critical, alarming=alarming, control=control,
                       maxsize=maxsize, maxdays=maxdays, maxlevel=maxlevel,
                       maxerrors=maxerrors)

        # Output shortcuts.
        self.console = self.root.console
        self.file = self.root.file

        # Set exit function.
        atexit.register(self._exit)

        pass

    def __repr__(self):
        """Get this Logger string representation."""
        return f'<Logger "{self._name}">'

    @property
    def name(self):
        """Get the unique logger name."""
        return self._name

    @property
    def with_error(self):
        """Get the flag indicating whether an error has occurred or not."""
        return self._with_error

    @property
    def count_errors(self):
        """Get the number of occurred errors."""
        return self._count_errors

    @property
    def all_errors(self):
        """Get the list with all currently met errors."""
        return self._all_errors

    def configure(self, app=None, desc=None, version=None, status=None,
                  console=None, file=None, email=None, html=None, table=None,
                  directory=None, filename=None, extension=None, smtp=None,
                  db=None, format=None, info=None, debug=None, warning=None,
                  error=None, critical=None, alarming=None, control=None,
                  maxsize=None, maxdays=None, maxlevel=None, maxerrors=None):
        """Configure this particular Logger.

        This is the only one right way to customize Logger. Parameters are the
        same as for instance creatrion.

        Parameters
        ----------
        app : str, optional
            The argument is used to set the `app` attribute.
        desc : str, optional
            The argument is used to set the `desc` attribute.
        version : str, optional
            The argument is used to set the `version` attribute.
        status : bool, optional
            The argument is used to open or close output `root`.
        console : bool, optional
            The argument is used to open or close output `console`.
        file : bool, optional
            The argument is used to open or close output `file`.
        email : bool, optional
            The argument is used to open or close output `email`.
        html : bool, optional
            The argument is used to open or close output `html`.
        table : bool, optional
            The argument is used to open or close output `table`.
        directory : str, optional
            The argument is used to set logging file folder.
        filename : str, optional
            The argument is used to set logging file name.
        extension : str, optional
            The argument is used to set logging file extension.
        smtp : dict, optional
            The argument is used to configure SMTP connection.
        db : dict, optional
            The argument is used to configure DB connection.
        format : str, optional
            The argument is used to set record template.
        info : bool, optional
            The argument is used to filter info records.
        debug : bool, optional
            The argument is used to filter debug records.
        warning : bool, optional
            The argument is used to filter warning records.
        error : bool, optional
            The argument is used to filter error records.
        critical : bool, optional
            The argument is used to filter critical records.
        alarming : bool, optional
            The argument is used to enable or disable alarming mechanism.
        control : bool, optional
            The argument is used to enable or disable execution break in case
            on error.
        maxsize : int or bool, optional
            The argument is used to define maximum size of output file.
        maxdays : int or bool, optional
            The argument is used to define maximum number of days that will be
            logged to same file.
        maxlevel : int or bool, optional
            The argument is used to define the break error level.
        maxerrors : int or bool, optional
            The argument is used to define maximun number of errors.
        """
        if isinstance(app, str) is True:
            self.app = app
        if isinstance(desc, str) is True:
            self.desc = desc
        if isinstance(version, (str, int, float)) is True:
            self.version = version

        # Create formatter in case it is not exists yet or just customize it.
        # Parameter format can be either string or dictionary.
        # When it is string then it must describe records format.
        # When it is dictionary it can contaion any parameter of formatter
        # that must be customized.
        if isinstance(format, str) is True:
            format = {'record': format}
        if hasattr(self, 'formatter') is False:
            format = {} if isinstance(format, dict) is False else format
            self.formatter = Formatter(**format)
        elif isinstance(format, dict) is True:
            self.formatter.configure(**format)

        # Create or customize record type filters.
        if hasattr(self, 'filters') is False:
            self.filters = {}
        for key, value in {'info': info, 'debug': debug, 'error': error,
                           'warning': warning, 'critical': critical}.items():
            if isinstance(value, bool) is True:
                self.filters[key] = value

        # Build the output root if it is not exists. In other case modify
        # existing output if it is requested.
        if hasattr(self, 'root') is False:
            self.root = Root(self, console=console, file=file, email=email,
                             html=html, table=table, status=status,
                             directory=directory, filename=filename,
                             extension=extension, smtp=smtp, db=db)
        else:
            for key, value in {'console': console, 'file': file,
                               'email': email, 'html': html,
                               'table': table}.items():
                if value is True:
                    getattr(self.root, key).open()
                    if key == 'file':
                        getattr(self.root, key).new()
                elif value is False:
                    getattr(self.root, key).close()

            # Customize output file path.
            path = {}
            if directory is not None:
                path['dir'] = directory
            if filename is not None:
                path['name'] = filename
            if extension is not None:
                path['ext'] = extension
            if len(path) > 0:
                self.root.file.configure(**path)

            # Customize SMTP server.
            if isinstance(smtp, dict) is True:
                self.root.email.configure(**smtp)

            # Customize database connection.
            if isinstance(db, dict) is True:
                self.root.table.configure(**db)

        # Customize limits and parameters of execution behaviour.
        if isinstance(maxsize, (int, float, bool)) is True:
            self._maxsize = maxsize
        if isinstance(maxdays, (int, float, bool)) is True:
            self._maxdays = maxdays
            self.__calculate_restart_date()
        if isinstance(maxlevel, (int, float, bool)) is True:
            self._maxlevel = maxlevel
        if isinstance(maxerrors, (int, float, bool)) is True:
            self._maxerrors = maxerrors
        if isinstance(alarming, bool) is True:
            self._alarming = alarming
        if isinstance(control, bool) is True:
            self._control = control

        # Initialize header instance when not exists.
        if hasattr(self, 'header') is False:
            self.header = Header(self)
        pass

    def write(self, record):
        """Direct write to the output.

        Parameters
        ----------
        record : Record
            The argument is used to send it to the output `root`.
        """
        self.__check_file_stats()
        self.root.write(record)
        pass

    def record(self, rectype, message, error=False, **kwargs):
        """Generate output record.

        Parameters
        ----------
        rectype : str
            By default method creates the record with the type NONE.
            That can be changed but depends on available record types.
            All registered record types are stored in the instance attribute
            rectypes. If you wish to use own record type or change the
            presentaion of exeisting one then edit this dictinary.
        message : str
            The message that must be written.
        error : bool, optional
            If record is error then set that parameter to `True`.
        **kwargs
            The keyword arguments used for additional forms (variables) for
            record and message formatting.
        """
        if self.filters.get(rectype, True) is True:
            record = Record(self, rectype, message, error=error, **kwargs)
            self.write(record)
        pass

    def info(self, message, **kwargs):
        """Send INFO record to output."""
        rectype = 'info'
        self.record(rectype, message, **kwargs)
        pass

    def debug(self, message, **kwargs):
        """Send DEBUG record to the output."""
        rectype = 'debug'
        self.record(rectype, message, **kwargs)
        pass

    def error(self, message=None, rectype='error', format=None, alarming=False,
              level=1, **kwargs):
        """Send ERROR record to the output.

        If exception in current traceback exists then method will format the
        exception according to `formatter.error` string presentation. If
        `formatter.error` is set to `False` the exception will be just printed
        in original Python style.
        Also method will send an alarm if alarming attribute is `True`, email
        output is enabled and SMTP server is configurated.
        If one of the limit triggers worked then application will be aborted.

        Parameters
        ----------
        message : str, optional
            The message that must be written instead of exception.
        rectype : str, optional
            The type of error according to `rectypes` dictionary.
        format : str, optional
            The format of the error message.
        alarming : bool
            The argument is used to enable or disable the alarming mechanism
            for this certain call.
        level : int
            The argument is used to describe the error level.
        **kwargs
            The keyword arguments used for additional forms (variables) for
            record and message formatting.
        """
        # Parse the error.
        err_type, err_value, err_tb = sys.exc_info()

        self._with_error = True
        self._count_errors += 1
        self._all_errors.append((err_type, err_value, err_tb))

        if message is None and err_type is not None:
            format = self.formatter.error if format is None else format
            if isinstance(format, str) is True:
                err_name = err_type.__name__
                err_value = err_value

                err_traceback = []
                raw = self.formatter.traceback
                for tb in traceback.walk_tb(err_tb):
                    f_code = tb[0].f_code

                    err_file = os.path.abspath(f_code.co_filename)
                    err_line = tb[1]
                    err_obj = f_code.co_name

                    new = raw.format(file=err_file, line=err_line, obj=err_obj)
                    err_traceback.append(new)
                err_traceback = ' '.join(err_traceback)

                self.record(rectype, message, error=True,
                            err_name=err_name, err_value=err_value,
                            err_traceback=err_traceback, **kwargs)
            elif format is False:
                exception = traceback.format_exception(err_type, err_value,
                                                       err_tb)
                message = '\n'
                message += ''.join(exception)
                self.record(rectype, message, **kwargs)
        else:
            message = message or ''
            self.record(rectype, message, **kwargs)

        # Break execution in case of critical error if permitted.
        # The alarm will be generated at exit if it is configured.
        if self._control is True:
            if level >= self._maxlevel:
                sys.exit()
            if self._maxerrors is not False:
                if self._count_errors > self._maxerrors:
                    sys.exit()

        # Send alarm if execution was not aborted but alarm is needed.
        if alarming is True:
            self.root.email.alarm()
        pass

    def warning(self, message=None, **kwargs):
        """Send WARNING error record to the output."""
        self.error(message, rectype='warning', level=0, **kwargs)
        pass

    def critical(self, message=None, **kwargs):
        """Send CRITICAL error record to the output."""
        self.error(message, rectype='critical', level=2, **kwargs)
        pass

    def head(self):
        """Send header to the output."""
        string = self.header.create()
        self.write(string)
        pass

    def subhead(self, string):
        """Send subheader to the output.

        Subheader is an upper-case text between two border lines.

        Parameters
        ----------
        string : str
            The text that will be presented as subheader.
        """
        bound = f'{self.formatter.div*self.formatter.length}\n'
        string = f'{bound}\t{string}\n{bound}'.upper()
        self.write(string)
        pass

    def line(self, message):
        """Send raw text with the new line to the output.

        Parameters
        ----------
        message : str
            The message that must be written.
        """
        self.write(f'{message}\n')
        pass

    def bound(self, div=None, length=None):
        """Write horizontal border in the output.

        Useful when need to separate different blocks of information.

        Parameters
        ----------
        div : str, optional
            Symbol that is used to bulid the bound.
        length : int, optional
            Lenght of the bound.
        """
        border = self.formatter.div * self.formatter.length
        self.write(border + '\n')
        pass

    def blank(self, number=1):
        """Write blank lines in the output.

        Parameters
        ----------
        number : int, optional
            The number of the blank lines that must be written.
        """
        string = '\n'*number
        self.write(string)
        pass

    def ok(self, **kwargs):
        """Print INFO message with OK."""
        rectype = 'info'
        message = self.messages['ok']
        self.record(rectype, message, **kwargs)
        pass

    def success(self, **kwargs):
        """Print INFO message with SUCCESS."""
        rectype = 'info'
        message = self.messages['success']
        self.record(rectype, message, **kwargs)
        pass

    def fail(self, **kwargs):
        """Print INFO message with FAIL."""
        rectype = 'info'
        message = self.messages['fail']
        self.record(rectype, message, **kwargs)
        pass

    def restart(self):
        """Restart logging. Will open new file."""
        self.start_date = dt.datetime.now()
        self.__calculate_restart_date()
        if self.root.file.status is True:
            self.root.file.new()
        if self.header.used is True:
            self.head()
        pass

    def email(self, *args, **kwargs):
        """Send email message.

        Note that SMTP server connection must be configured.
        """
        self.root.email.send(*args, **kwargs)
        pass

    def table(self, **kwargs):
        """Write information to database table.

        Note that DB connection must be configured.
        """
        self.root.table.write(**kwargs)
        pass

    def _exit(self):
        # Inform about the error.
        if self._alarming is True and self._with_error is True:
            self.root.email.alarm()
        pass

    def __calculate_restart_date(self):
        # Calculate the date when logger must be restarted according to
        # maxdays parameter.
        self.__restart_date = (self.start_date
                               + dt.timedelta(days=self._maxdays))
        pass

    def __check_file_stats(self):
        # Check the output file statistics to catch when current file must be
        # closed and new one must be opened.
        if self.root.file.status is True:
            if self._maxsize is not False:
                if self.root.file.size is not None:
                    if self.root.file.size > self._maxsize:
                        self.restart()
                        return
            if self._maxdays is not False:
                if self.__restart_date.day == dt.datetime.now().day:
                    self.restart()
                    return
