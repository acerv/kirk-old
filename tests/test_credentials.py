"""
Test credentials module
"""
import os
import pytest
import kirk.credentials

CREDENTIALS = "credentials.cfg"


@pytest.fixture(autouse=True)
def remove_file():
    if os.path.isfile(CREDENTIALS):
        os.remove(CREDENTIALS)


def test_get_set_password():
    """
    Test set_password and get_password methods
    """
    kirk.credentials.set_password(
        CREDENTIALS, "jenkins.xyz.org", "kirk", "12345")
    assert os.path.isfile(CREDENTIALS)

    password = kirk.credentials.get_password(
        CREDENTIALS, "jenkins.xyz.org", "kirk")
    assert password == "12345"
