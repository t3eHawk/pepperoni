"""Elements used for record preparation and creation."""

import datetime as dt
import os
import sys
import threading


class Record():
    """Represents a particular logging record as an object.

    This class describes the record. Record is an entity that is going to
    be send to the output as a single and separated string.
    Main purpose of the record is to return formatted string based on two level
    string templates and set of the forms - variables used in string
    formatting.
    First level string template presents a whole record formatting including
    message.
    Second level string template present only message format.
    Also there are two types of forms. First one is predifined dynamic forms
    which are the variablse that automatically defined by class during the
    instance construction. Second one is user defined forms which are passed
    to class constructor as kwargs.
    List of predefined dynamic forms available by now:

    +---------+----------------------------------------------------+
    |  Name   |                 Description                        |
    +=========+====================================================+
    |rectype  |Type of the record                                  |
    +---------+----------------------------------------------------+
    |datetime |Datetime object at the time of record construction  |
    +---------+----------------------------------------------------+
    |isodate  |Date string form of the time of record construction |
    +---------+----------------------------------------------------+
    |objname  |Name of the object from which record was initiated  |
    +---------+----------------------------------------------------+
    |flname   |Script file name from which record was initiated    |
    +---------+----------------------------------------------------+
    |thread   |Current thread name                                 |
    +---------+----------------------------------------------------+
    |div      |Border element                                      |
    +---------+----------------------------------------------------+
    |message  |Input text message                                  |
    +---------+----------------------------------------------------+

    Parameters
    ----------
    logger : Logger
        That is a Logger object that owns the output for that record.
    rectype : str
        Name of the record type item from the Logger.rectypes dictionary.
    message : str
        Input message that must be printed with that record.
    error : bool, optional
        That is True or False to indicate that record include error
        information.
    format : str, optional
        String template of the whole record.
    error_format : str or bool, optional
        String template of the error message.
    **kwargs
        The keyword arguments that is used for additional variables in record
        and message formatting.
    """

    def __init__(self, logger, rectype, message, error=False, format=None,
                 error_format=None, **kwargs):
        self.logger = logger
        # Get the record string template.
        self.format = format or logger.formatter.record
        # Get the presentation of record type.
        self.rectype = logger.rectypes[rectype]

        # Date forms.
        self.datetime = dt.datetime.now()
        self.isodate = self.datetime.isoformat(sep=' ', timespec='seconds')

        # Execution forms.
        frame = self.__catch_frame()
        f_code = frame.f_code
        flname = f_code.co_filename
        objname = f_code.co_name
        self.objname = objname if objname != '<module>' else 'main'
        self.flname = os.path.splitext(os.path.basename(flname))[0]
        self.thread = threading.current_thread().name

        # Styling forms.
        self.div = logger.formatter.div

        # Store formatted message as instance attribute.
        message = str(message if error is False else logger.formatter.error)
        try:
            self.message = message.format(**self.__dict__, **kwargs)
        except KeyError:
            self.message = message
        pass

    def __str__(self):
        """Create record string."""
        return self.create()

    __repr__ = __str__

    def create(self, css=False):
        """Create and return string representation of the record."""
        string = self.format.format(**self.__dict__)
        return string

    def __catch_frame(self):
        """Catch the frame from file where methods of module was called."""
        frame = sys._getframe()
        module_dir = os.path.dirname(__file__)
        while True:
            if module_dir != os.path.dirname(frame.f_code.co_filename):
                return frame
            else:
                frame = frame.f_back
