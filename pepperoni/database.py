"""Database tools.

Contains tools that makes work with database much easier and faster.
Based on SQLAlchemy.
"""

import os
import sys
import sqlalchemy as sql


class Database():
    """Class represent database as an object.

    This class includes methods and elements that makes work with database
    much easier and faster.

    Parameters
    ----------
    vendor : str, optional
        Name of the database provider e.g. oracle, mysql, postgresql.
        This argument can be skipped only if engine argument is going to be
        used instead.
        Refer to SQLAlchemy Engine Configuration document to see supported
        values.
    driver : str, optional
        Name of the database driver used for connection.
        Refer to SQLAlchemy Engine Configuration document to see supported
        values.
    path : str, optional
        Path to the database instance. Currently available only for SQLite.
    host : str, optional
        Name or IP address of the host on which database is running.
    port : str or int, optional
        Port on which database can be accessed.
    sid : str, optional
        Database SID.
    service : str, optional
        Database service name.
    user : str, optional
        Username used to login into the database.
    password : str, optional
        Password used to login into the database.
    engine : sqlalchemy.Engine
        Database engine object.

    Attributes
    ----------
    vendor : str
        Name of the database provider.
    driver : str
        Name of the database driver used for connection.
    path : str
        Path to the database instance.
    host : str
        Name or id address of the host on which database is running.
    port : str or int
        Port on which database is running.
    sid : str
        Database SID.
    service : str
        Database service name.
    user : str
        Username used to login into the database.
    engine : sqlalchemy.Engine
        Database engine object.
    ckwargs : dict
        Default SQL compilation keyword arguments.
    """

    def __init__(self, vendor=None, driver=None, engine=None, path=None,
                 host=None, port=None, sid=None, service=None,
                 user=None, password=None):
        self.vendor = None
        self.driver = None
        self.engine = None
        self.path = None
        self.host = None
        self.port = None
        self.sid = None
        self.service = None
        self.user = None

        self.ckwargs = {'literal_binds': True}

        # Database vendor name must be only a string.
        if vendor is not None and isinstance(vendor, str) is False:
            raise AttributeError('incorrect vendor name')
        self.vendor = vendor

        # Database driver name must be only a string.
        if driver is not None and isinstance(driver, str) is False:
            raise AttributeError('incorrect driver name')
        self.driver = driver

        # Connection url for sqlite little bit differ from other databases.
        if vendor == 'sqlite':
            # Path to database instance must be only a string.
            if path is not None and isinstance(path, str) is False:
                raise AttributeError('incorrect path')
            path = os.path.abspath(path) if path is not None else path
            self.path = path

            # For in memory SQLite instance.
            if path is None:
                url = f'{vendor}://'
            # On Windows three slashes must be used.
            elif sys.platform.startswith('win'):
                url = f'{vendor}:///{path}'
            else:
                url = f'{vendor}:////{path}'
        elif vendor is not None:
            # You cannot login to unknown host.
            if host is not None and isinstance(host, str) is False:
                raise AttributeError('incorrect host')
            self.host = host

            # You cannot login without knowing the port.
            if port is not None and isinstance(port, (str, int)) is False:
                raise AttributeError('incorrect port')
            self.port = port

            if sid is not None or service is not None:
                # SID can be only a string.
                if sid is not None and isinstance(sid, str) is False:
                    raise AttributeError('incorrect sid')
                self.sid = sid

                # Service name can be only a string.
                if service is not None and isinstance(service, str) is False:
                    raise AttributeError('incorrect service')
                self.service = service
            else:
                raise AttributeError('neither SID nor Service name are known')

            # You need an account to login.
            if user is not None and isinstance(user, str) is False:
                raise AttributeError('can not login without a username')
            self.user = user

            # Login without a password is prohibited.
            if isinstance(password, str) is False:
                raise AttributeError('can not loging without a password')

            credentials = f'{user}:{password}'
            address = f'{host}:{port}'
            id = sid if sid is not None else f'?service_name={service}'
            if driver is None:
                url = f'{vendor}://{credentials}@{address}/{id}'
            else:
                url = f'{vendor}+{driver}://{credentials}@{address}/{id}'

        if isinstance(engine, sql.engine.base.Engine) is True:
            self.engine = engine
        else:
            self.engine = sql.create_engine(url)
        pass

    def connect(self):
        """Get database connection.

        Returns
        -------
        connection : sqlalchemy.Connection
            Database connection instance.
        """
        return self.engine.connect()

    def table(self, name):
        """Get database table.

        Returns
        -------
        table : sqlalchemy.Table
            Database table instance.
        """
        meta = sql.MetaData()
        return sql.Table(name, meta, autoload=True, autoload_with=self.engine)
