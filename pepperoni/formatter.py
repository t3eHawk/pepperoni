

class Formatter():
    """This class represents formatter - object that defines the format of the
    output records.

    Parameters
    ----------
    record : str, optional
        Format of the output record.
    error : str, optional
        Format of the error message.
    length : int, optional
        Basic length of line in output.
    div : str, optional
        Text symbol used for borders and blocks.
    """

    def __init__(self, record=None, error=None, length=80, div='*'):
        def_record = '{isodate}\t{rectype}\t{message}\n'
        def_error = '{err_name}\t{err_value}\t{err_file}\t{err_line}\t{err_obj}'

        record = record or def_record
        error = def_error if error is None else error

        self.configure(record=record, error=error, length=length, div=div)
        pass

    def configure(self, record=None, error=None, length=None, div=None):
        """Configure Formatter instance parameters.

        Parameters
        ----------
        record : str, optional
            Format of the output record.
        error : str, optional
            Format of the error message.
        length : int, optional
            Basic length of line in output.
        div : str, optional
            Text symbol used for borders and blocks.
        """
        if record is not None: self.record = record
        if error is not None: self.error = error
        if length is not None: self.length = length
        if div is not None: self.div = div
        pass
