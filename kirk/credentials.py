"""
.. module:: credentials
   :platform: Multiplatform
   :synopsis: module handling credentials
   :license: GPLv2
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
from keyrings.cryptfile.cryptfile import CryptFileKeyring

inkr = CryptFileKeyring()


def get_password(file_path, section, username):
    """
    Return a password stored inside the keyrings file.
    :param file_path: keyrings file path
    :type file_path: str
    :param section: section of the username
    :type section: str
    :param username: user name
    :type username: str
    :return: password as string
    """
    inkr.file_path = file_path
    password = inkr.get_password(section, username)
    return password


def set_password(file_path, section, username, password):
    """
    Set the user password inside keyrings file.
    :param file_path: keyrings file path
    :type file_path: str
    :param section: section of the username
    :type section: str
    :param username: user name
    :type username: str
    :param password: user password
    :type username: str
    """
    inkr.file_path = file_path
    password = inkr.set_password(section, username, password)
