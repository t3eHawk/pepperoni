"""Elements reflecting output objects."""

import datetime as dt
import functools
import os
import smtplib
import sqlalchemy as sql

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .database import Database
from .record import Record
from .utils import py_dir


def you_shall_not_pass(func):
    """Prevent access to an inactive output."""
    @functools.wraps(func)
    def wrapper(output, *args, **kwargs):
        if output.status is True:
            func(output, *args, **kwargs)
    return wrapper


class Output():
    """Parent class for all outputs.

    Parameters
    ----------
    status : bool, optional
        Used to open or close the output.

    Arguments
    ---------
    status : bool
        Status for this particular output.
    """

    def __init__(self, status=False):
        self._status = status
        pass

    @property
    def status(self):
        """Get output status."""
        return self._status

    def open(self):
        """Make this output active."""
        self._status = True
        pass

    def close(self):
        """Make this output inactive."""
        self._status = False
        pass


class Branch(Output):
    """Output branch.

    Parent class for each low-level output object e.g. console, file, email,
    database table, and HTML document.

    Parameters
    ----------
    root : Output
        Used to set `root` attribute.
    status : bool
        The argument that is used to enable or disable output.

    Attributes
    ----------
    root : Root
        Low-level output that is a root of this branch.
    status : bool
        Status for this particular output.
    """

    def __init__(self, root, status=False):
        super().__init__(status=status)
        self._root = root
        pass

    @property
    def root(self):
        """Low-level output that is a root of this branch."""
        return self._root


class Root(Output):
    """Output root.

    This class represents the output root - low-level output object that is
    literally a bridge between logger inputs and high-level outputs like
    console. file, email, database table and HTML document.

    Constructor of this class also creates high-level outputs as `Root`
    attributes like `console`, `file`, `email`, `html` and `table`.

    Parameters
    ----------
    logger : Logger
        The `Logger` that owns that output root.
    status : bool, optional
        Used to open or close the output.
    console : bool, optional
        Used for `status` argument of `Console` class.
    file : bool, optional
        Used for `status` argument of `File` class.
    email : bool, optional
        Used for `status` argument of `Email` class.
    html : bool, optional
        Used for `status` argument of `HTML` class.
    table : bool, optional
        Used for `status` argument of `Table` class.
    status : bool, optional
        The overall status of the `Root`.
    directory : str, optional
        Used for `dir` argument of `File` class.
    filename : str, optional
        Used for `name` argument of `File` class.
    extension : str, optional
        Used for `extension` argument of `File` class.
    smtp : dict, optional
        Used to pass `address`, `host`, `port`, `tls`, `user`,
        `password` and `recipients` arguments to `Email` class.
    db : dict, optional
        Used to pass `vendor`, `host`, `port`, `sid`, `user`,
        `password`, `schema`, `table`, `proxy`, `db` and `date_column`
        arguments to `Table` class.

    Attributes
    ----------
    status : bool
        Status for this particular output.
    logger : Logger
        The `Logger` object that owns that output.
    console : Console
        The `Console` object output.
    file : File
        The `File` object output.
    email : Email
        The `Email` object output.
    html : HTML
        The `HTML` object output.
    table : Table
        The `Table` object output.
    """

    def __init__(self, logger, status=True, console=True, file=True,
                 email=False, html=False, table=False, directory=None,
                 filename=None, extension=None, smtp=None, db=None):
        super().__init__(status=status)
        self.logger = logger

        self.console = Console(self, status=console)

        path = dict(dir=directory, name=filename, ext=extension)
        self.file = File(self, status=file, **path)

        self.html = HTML(self, status=html)

        smtp = smtp if isinstance(smtp, dict) is True else {}
        self.email = Email(self, status=email, **smtp)

        db = db if isinstance(db, dict) is True else {}
        self.table = Table(self, status=table, **db)
        pass

    @you_shall_not_pass
    def write(self, record):
        """Send received record to all writable outputs.

        Parameters
        ----------
        record : str or Record
            The data that must be written to writable outputs.
        """
        if isinstance(record, Record) is True:
            record = record.create()
        self.console.write(record)
        self.file.write(record)
        self.html.write(record)
        pass


class Console(Branch):
    """Represents console output.

    Parameters
    ----------
    root : Output
        Used to set `root` attribute.
    status : bool
        The argument that is used to enable or disable output.

    Attributes
    ----------
    root : Root
        Low-level output that is a root of this branch.
    status : bool
        Status for this particular output.
    """

    @you_shall_not_pass
    def write(self, record):
        """Write string to console.

        Parameters
        ----------
        record : str
            The string that must be written to system stdout.
        """
        print(record, end='')
        pass


class File(Branch):
    """Represents file output.

    Parameters
    ----------
    root : Output
        Used to set `root` attribute.
    status : bool, optional
        Used to open or close the output.
    dir : str, optional
        Used to set `dir` attribute.
    name : str, optional
        Used to set `name` attribute.
    ext : str, optional
        Used to set `ext` attribute.

    Attributes
    ----------
    root : Root
        Low-level output that is a root of this branch.
    status : bool
        Status for this particular output.
    dir : str
        The path to folder in which output file must be created.
        By default we use the *logs* folder in current location.
    name : str
        The name of output file. By default we use the string representing
        the start date of logging in format *YYYYMMDDHHMISS*.
    ext : str
        The extension of output file. By default we use *log* extension.
    """

    def __init__(self, root, status=True, dir=None, name=None, ext=None):
        super().__init__(root, status=status)
        dir = dir or os.path.join(py_dir, 'logs')
        name = name or '{root.logger.start_date:%Y%m%d%H%M%S}'
        ext = ext or 'log'
        self.configure(dir=dir, name=name, ext=ext)
        pass

    @property
    def path(self):
        """Return absolute path to output file."""
        return self._path

    @property
    def modified(self):
        """Return last time when file was modified."""
        return self._modified

    @property
    def size(self):
        """Return current file size."""
        return self._size

    def configure(self, dir=None, name=None, ext=None):
        """Change output file parameters.

        Parameters
        ----------
        dir : str, optional
            Used to define path to folder in which output file
            must be created. By default it will be the *logs* folder in current
            location.
        name : str, optional
            Used to define the name of output file. By default
            it will be the string representing the start date of logging in
            format *YYYYMMDDHHMISS*.
        ext : str, optional
            Used to define the extension of output file. By
            default we use *log* extension.
        """
        if isinstance(dir, str) is True:
            self.dir = dir
        if isinstance(name, str) is True:
            self.name = name
        if isinstance(ext, str) is True:
            self.ext = ext
        if dir is not None or name is not None or ext is not None:
            self.new()
        pass

    @you_shall_not_pass
    def new(self):
        """Open new output file."""
        # Define new path.
        head = self.dir
        tail = f'{self.name}.{self.ext}'
        datetime = self.root.logger.start_date
        path = os.path.join(head, tail)
        self._path = path.format(root=self.root, datetime=datetime)

        # Handler and file statistics must be purged.
        self.__handler = None
        self._modified = None
        self._size = None
        pass

    @you_shall_not_pass
    def write(self, record):
        """Write data to output file.

        Built-in Python file handling will be used.
        This method will also:
            - Creating output file path if it is not exists yet.
            - Updating output file modify time and current size attributes.

        Parameters
        ----------
        record : str
            The string that must be written to file.
        """
        # Create path and open file handler if it is not opened yet.
        if self.__handler is None:
            # Check the directories.
            dirname = os.path.dirname(self._path)
            if os.path.exists(dirname) is False:
                os.makedirs(dirname)
            # Make file.
            self.__handler = open(self._path, 'a')

        # We should write to handler only string values.
        # So if data presented as record.Record() object it must be converted
        # to string value by using Record.create() method.
        self.__handler.write(record)
        self.__handler.flush()

        # Update statistics that is requeired for other logger functionality.
        self._modified = dt.datetime.now()
        self._size = os.stat(self._path).st_size
        pass


class Email(Branch):
    """Represents email output.

    Gives access to SMTP server and email objects used to send messages,
    notifications and alarms.

    Parameters
    ----------
    root : Output
        Used to set `root` attribute.
    status : bool, optional
        Used to open or close the output.
    address : str, optional
        Used to set the `email` attribute.
    host : str, optional
        Used to set the `host` attribute.
    port : str or int, optional
        Used to set the `port` attribute.
    tls : bool, optional
        Used to set `tls` attribute.
    user : str, optional
        Used to set `user` attribute.
    password : str, optional
        Used to pass `password` argument to `connect()` method.
    recipients : str or list, optional
        Used to set `recipients` attribute.

    Attributes
    ----------
    root : Root
        Low-level output that is a root of this branch.
    status : bool
        Status for this particular output.
    address : str
        The email address using to send messages.
    host : str
        The host on which SMTP server is running.
    port : str or int, optional
        The port on which SMTP server can be reached.
    tls : bool
        The flag of TLS channel enabled.
    user : str
        The username using to login to SMTP server.
    recipients : str or list
        The one or more email addresses who will receive the messages.
    """

    def __init__(self, root, status=False, address=None, host=None, port=None,
                 tls=None, user=None, password=None, recipients=None):
        super().__init__(root, status=status)
        self.address = None
        self.host = None
        self.port = None
        self.tls = None
        self.user = None
        self.password = None
        self.recipients = None
        self.configure(address=address, host=host, port=port, tls=tls,
                       user=user, password=password, recipients=recipients)
        pass

    def configure(self, address=None, host=None, port=None, tls=None,
                  user=None, password=None, recipients=None):
        """Configure SMTP server connection and email parameters.

        Parameters
        ----------
        address : str, optional
            Used to set the `email` attribute.
        host : str, optional
            Used to set the `host` attribute.
        port : str or int, optional
            Used to set the `port` attribute.
        tls : bool, optional
            Used to set `tls` attribute.
        user : str, optional
            Used to set `user` attribute.
        password : str, optional
            Used to pass `password` argument to `connect()`
            method.
        recipients : str or list, optional
            Used to set `recipients` attribute.
        """
        if isinstance(host, str) is True:
            self.host = host
        if isinstance(port, int) is True:
            self.port = port
        if isinstance(tls, bool) is True:
            self.tls = tls

        if isinstance(user, str) is True:
            self.user = user
        if isinstance(address, str) is True:
            self.address = address
        if isinstance(recipients, (str, list)) is True:
            if isinstance(recipients, str) is True:
                if ',' in recipients:
                    recipients = recipients.replace(' ', '').split(',')
                else:
                    recipients = [recipients]
            self.recipients = recipients

        if (host is not None or port is not None or
            user is not None or password is not None):
            try:
                self.connect(password)
            except Exception:
                self.root.logger.warning()
                self._status = False
        pass

    @you_shall_not_pass
    def connect(self, password):
        """Connect to SMTP server.

        Parameters
        ----------
        password : str
            Used as password in SMTP server connection.
        """
        # You cannot connect to unknown host.
        if (hasattr(self, 'host') is False or
            isinstance(self.host, str) is False):
            raise AttributeError('incorrect host')

        # You must connect to certain port.
        if (hasattr(self, 'port') is False or
            isinstance(self.port, int) is False):
            raise AttributeError('incorrect port')

        # Creating connection with or without TLS.
        self._server = smtplib.SMTP(self.host, self.port)
        if self.tls is True:
            self._server.starttls()

        # Login to server.
        if self.user is not None:
            if password is None:
                raise AttributeError('can not login without a password')

            self._server.login(self.user, password)
        pass

    @you_shall_not_pass
    def disconnect(self):
        """Disconnect from SMTP server."""
        if hasattr(self, '_server') is True:
            self._server.quit()
        pass

    @you_shall_not_pass
    def send(self, subject, text, recipients=None, attachment=None,
             type='html'):
        """Send regular message to the listed email addresses.

        Parameters
        ----------
        subject : str
            Used for message subject.
        text : str, MIMEText, list of str or list of MIMEText
            Used for messages text.
        recipients : str or list, optional
            Used for message receivers.
        attachment : str or list of str, optional
            Used for path to message attachment.
        type : str, optional
            The argument for MIMEText as _subtype. So actually it defines the
            type of the whole message (e.g. HTML).
        """
        # Message from.
        sender = self.address
        # Mesasge to. Must be a string with list of email addresses separated
        # with comma.
        recipients = recipients or self.recipients
        # Message can be send only when there is at least one recipient.
        if recipients is not None:
            if isinstance(recipients, list) is True:
                recipients = ', '.join(recipients)

            message = MIMEMultipart()
            message['From'] = sender
            message['To'] = recipients
            message['Subject'] = subject

            # Message is MIMEMultipart so text must be attached as a part.
            if text is not None:
                if isinstance(text, list) is False:
                    text = [text]
                for item in text:
                    if isinstance(item, MIMEText) is False:
                        item = MIMEText(item, _subtype=type)
                    message.attach(item)

            # Now include all attachments.
            if attachment is not None:
                if isinstance(attachment, list) is False:
                    attachment = [attachment]
                for item in attachment:
                    filename = os.path.basename(item)
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(open(item, "rb").read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition",
                                    f"attachment; filename={filename}")
                    message.attach(part)

            # Finally send message.
            self._server.send_message(message)
        pass

    @you_shall_not_pass
    def alarm(self, with_log=True):
        """Send special alarm message.

        That message has the name of the application in the subject, log
        header in the text and also log file as an attahcment if it is enabled
        and if parameter with_log is set to True.
        That method is a generic way used in Logger write methods to inform
        user about occured application errors. But it also can be used by
        user outside of the errors.

        Parameters
        ----------
        with_log : bool, optional
            Used for attachment of logging output file to
            the alarm message. The default is True.
        """
        subject = f'ALARM in {self.root.logger.app}!'

        text = self.root.logger.header.create()
        text = f'<pre>{text}</pre>'
        text = MIMEText(text, 'html')

        if with_log is True and self.root.file.status is True:
            attachment = self.root.file.path
        else:
            attachment = None

        self.send(subject, text, recipients=self.recipients,
                  attachment=attachment)
        pass

    @you_shall_not_pass
    def write(self, record):
        """Write record (not used)."""
        pass


class HTML(Branch):
    """Represents HTML document output.

    Can be used when you need to style your logs or to display them on
    some web application like dashboard.
    """

    def __init__(self, root, status=False, dir=None, filename=None):
        super().__init__(root, status=status)
        pass

    def configure(self, dir=None, filename=None):
        """Configure HTML document output."""
        pass

    @you_shall_not_pass
    def write(self, record):
        """Write record (not used)."""
        pass


class Table(Branch):
    """Represents a database table output.

    Can be used to generate record in database table and update its fields
    with necessary values during the logging process.

    Parameters
    ----------
    root : Output
        Used to set `root` attribute.
    status : bool, optional
        Used to open or close the output.
    date_column : str, optional
        Used to set `date_column` attribute.

    Attributes
    ----------
    root : Root
        Low-level output that is a root of this branch.
    status : bool
        Status for this particular output.
    date_column : str
        Name of the column in logging table which can be modified by
        application to write last write date.
    """

    def __init__(self, root, status=False, name=None, database=None,
                 proxy=None, date_column=None, **kwargs):
        super().__init__(root, status=status)
        self.name = None
        self.database = None
        self.date_column = None
        self._primary_key = None
        self._primary_key_column = None

        self.configure(name=name, database=database, proxy=proxy,
                       date_column=date_column)
        pass

    # Used for a compatibility with version 0.1.1.
    @property
    def db(self):
        """Return database connection object."""
        return self.database.connect()

    @property
    def primary_key(self):
        """Return primary key of actual table logging record."""
        return self._primary_key

    def configure(self, name=None, database=None, proxy=None,
                  date_column=None, **kwargs):
        """Configure database and table.

        Parameters
        ----------
        date_column : str, optional
            Used to set `date_column` attribute.
        """
        if isinstance(name, str) is True:
            self.name = name.lower()

        # Here is a creating of database connection.
        if isinstance(self.database, Database) is False:
            if isinstance(database, Database) is True:
                self.database = database
            else:
                vendor = kwargs.get('vendor')
                engine = kwargs.get('engine')
                if vendor is not None:
                    db_kwargs = {}
                    if engine is not None:
                        db_kwargs['engine'] = engine
                    else:
                        db_kwargs['host'] = kwargs.get('host')
                        db_kwargs['port'] = kwargs.get('port')
                        db_kwargs['sid'] = kwargs.get('sid')
                        db_kwargs['service'] = kwargs.get('service')
                        db_kwargs['path'] = kwargs.get('path')
                        db_kwargs['user'] = kwargs.get('user')
                        db_kwargs['password'] = kwargs.get('password')
                    self.database = Database(vendor, **db_kwargs)
        # Check database connection.
        if self.database is not None:
            try:
                conn = self.database.connect()
                conn.close()
            except Exception:
                self.root.logger.warning()
                self._status = False
            else:
                # Here is a table declaration.
                if isinstance(proxy, sql.sql.schema.Table) is True:
                    self.name = proxy.name
                    self.proxy = proxy
                elif isinstance(name, str) is True:
                    self.name = name
                    self.proxy = self.database.table(name)
                else:
                    tp = name.__class__.__name__
                    raise TypeError(f'name must str not {tp}')

                if isinstance(date_column, str) is True:
                    self.date_column = date_column

                self._primary_key_column = self._get_primary_key_column()
                self._primary_key = None
        pass

    @you_shall_not_pass
    def new(self):
        """Initiate new logging record."""
        self._primary_key = None
        pass

    @you_shall_not_pass
    def write(self, **values):
        """Write to logging table.

        In case of date_column was defined then its value will be refreshed.
        In case of no record was created before then the new one will be
        inserted to table. in other case record by known primary_key will be
        updated.

        Parameters
        ----------
        **values
            The keyword argument is used to update fields in table.
        """
        conn = self.database.connect()
        if self.date_column is not None:
            values[self.date_column] = dt.datetime.now()
        if self._primary_key is None:
            insert = self.proxy.insert().values(**values)
            result = conn.execute(insert)
            self._primary_key = result.inserted_primary_key[0]
        else:
            update = self.proxy.update().\
                values(**values).\
                where(self._primary_key_column == self._primary_key)
            conn.execute(update)
        conn.close()
        pass

    def _get_primary_key_column(self):
        if isinstance(self.proxy, sql.sql.schema.Table) is True:
            primary_key_columns = list(self.proxy.primary_key)
            ln = len(primary_key_columns)
            if ln == 1:
                primary_key_column = primary_key_columns[0]
                return primary_key_column
            else:
                raise ValueError(f'primary key number should be 1 not {ln}')
