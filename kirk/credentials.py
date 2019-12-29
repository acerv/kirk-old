"""
.. module:: credentials
   :platform: Multiplatform
   :synopsis: module handling credentials
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
from keyring.errors import KeyringError
from keyrings.alt.file import PlaintextKeyring
from kirk import KirkError


class Credentials:
    """
    Base class for a credentials handler.
    """

    def get_password(self, section, username):
        """
        Return a password stored inside the keyrings file.

        Args:
            section(str): section of the ``username``.
            username(str): user name we want to get password.

        Returns:
            str: ``username`` password.

        Raises:
            :py:class:`KirkError`: raised if an error occurs.
        """
        raise NotImplementedError()

    def set_password(self, section, username, password):
        """
        Set the ``username`` password inside keyrings file.

        Args:
            section(str): section of the ``username``.
            username(str): user name we want to set ``password``.
            password(str): password of the ``username``.

        Raises:
            :py:class:`KirkError`: raised if an error occurs.
        """
        raise NotImplementedError()


class CredentialsHandler(Credentials):
    """
    Inherit :py:class:`Credentials` and save/load credentials from a
    keyrings file.
    """

    def __init__(self, file_path):
        """
        Args:
            file_path(str): keyrings file path.
        """
        self._file_path = file_path
        self._inkr = PlaintextKeyring()

    def get_password(self, section, username):
        password = ""
        try:
            self._inkr.file_path = self._file_path
            password = self._inkr.get_password(section, username)
        except KeyringError as err:
            raise KirkError(err)

        return password

    def set_password(self, section, username, password):
        try:
            self._inkr.file_path = self._file_path
            self._inkr.set_password(section, username, password)
        except KeyringError as err:
            raise KirkError(err)
