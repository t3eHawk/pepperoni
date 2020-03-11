"""Special configurator for credentials."""

import configparser
import json
import os


class Credentials():
    """Class reflects special configurator for credentials.

    It helps to move your confidential information from scripts to separate
    files in user directory.
    It will parse files ~/.pepperoni/credentials.[ini/json] and store
    information in format {<name>: {<user>: <value>, <password>: <value>}}.

    File credentials.ini should look like:
    [tatooine]
    user=kenobi
    password=May4BeWithYou

    [dagobah]
    user=yoda
    password=DoOrDoNotThereIsNoTry

    File credentials.json should look like:
    {
      "tatooine": {"user": "kenobi", password: "May4BeWithYou"},
      "dagobah": {"user": "yoda", "password": "DoOrDoNotThereIsNoTry"}
    }

    If name is being duplicated in both files then the values from the INI file
    will be used.
    """

    def __init__(self):
        self.__data = data = {}

        path = os.path.expanduser('~/.pepperoni/credentials.ini')
        if os.path.exists(path) is True:
            config = configparser.ConfigParser()
            config.read(path)
            for section in config.sections():
                data[section.lower()] = {}
                data[section]['user'] = config[section].get('user')
                data[section]['password'] = config[section].get('password')

        path = os.path.expanduser('~/.pepperoni/credentials.json')
        if os.path.exists(path) is True:
            try:
                with open(path, 'r') as fh:
                    config = json.load(fh)
                    for key, value in config.items():
                        data[key.lower()] = {}
                        data[key]['user'] = value.get('user')
                        data[key]['password'] = value.get('password')
            except Exception:
                pass
        pass

    def __repr__(self):
        """Get string with credential names."""
        return str(list(self.__data.keys()))

    def __getitem__(self, key):
        """Get credentials dictionary.

        Returns
        -------
        dict : dict
            Dictionary containing keys: user, password.
        """
        return self.__data.get(key)

    def get(self, key):
        """Get credentials dictionary if exists.

        Returns
        -------
        dict : dict
            Dictionary containing keys: user, password.
        """
        return self.__data.get(key)
