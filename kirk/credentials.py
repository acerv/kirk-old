"""
.. module:: credentials
   :platform: Multiplatform
   :synopsis: module handling credentials
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
from keyrings.alt.file import PlaintextKeyring


class Credentials:
    """
    Base class for a credentials handler
    """

    def get_password(self, section, username):
        """
        Return a password stored inside the keyrings file.
        :param section: section of the username
        :type section: str
        :param username: user name
        :type username: str
        :return: password as string
        """
        raise NotImplementedError()

    def set_password(self, section, username, password):
        """
        Set the user password inside keyrings file.
        :param section: section of the username
        :type section: str
        :param username: user name
        :type username: str
        :param password: user password
        :type username: str
        """
        raise NotImplementedError()


class PlaintextCredentials(Credentials):
    """
    Save/Load credentials from a plaintext file.
    """

    def __init__(self, file_path):
        """
        :param file_path: keyrings file path
        :type file_path: str
        """
        self._file_path = file_path
        self._inkr = PlaintextKeyring()

    def get_password(self, section, username):
        """
        Return a password stored inside the keyrings file.
        :param section: section of the username
        :type section: str
        :param username: user name
        :type username: str
        :return: password as string
        """
        self._inkr.file_path = self._file_path
        password = self._inkr.get_password(section, username)
        return password

    def set_password(self, section, username, password):
        """
        Set the user password inside keyrings file.
        :param section: section of the username
        :type section: str
        :param username: user name
        :type username: str
        :param password: user password
        :type username: str
        """
        self._inkr.file_path = self._file_path
        password = self._inkr.set_password(section, username, password)
