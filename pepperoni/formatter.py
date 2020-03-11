"""Output records formatter."""


class Formatter():
    """Output records formatter.

    Class represents output records format.

    Parameters
    ----------
    record : str, optional
        Format of the output record.
    error : str, optional
        Format of the error message.
    traceback : str, optional
        Format of the traceback string.
    length : int, optional
        Basic length of line in output.
    div : str, optional
        Text symbol used for borders and blocks.
    """

    def __init__(self, record=None, error=None, traceback=None,
                 length=80, div='*'):
        def_record = '{isodate}\t{rectype}\t{message}\n'
        def_error = '{err_name}: {err_value}. {err_traceback}'
        def_traceback = 'File {file}, line {line}, in {obj}.'

        record = record or def_record
        error = def_error if error is None else error
        traceback = def_traceback if traceback is None else traceback

        self.configure(record=record, error=error, traceback=traceback,
                       length=length, div=div)
        pass

    def configure(self, record=None, error=None, traceback=None,
                  length=None, div=None):
        """Configure Formatter instance parameters.

        Parameters
        ----------
        record : str, optional
            Format of the output record.
        error : str, optional
            Format of the error message.
        trace : str, optional
            Format of the traceback string.
        length : int, optional
            Basic length of line in output.
        div : str, optional
            Text symbol used for borders and blocks.
        """
        if record is not None:
            self.record = record
        if error is not None:
            self.error = error
        if traceback is not None:
            self.traceback = traceback
        if length is not None:
            self.length = length
        if div is not None:
            self.div = div
        pass
