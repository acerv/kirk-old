"""
Test credentials module
"""
import pytest
import keyring.errors
import keyrings.alt.file
from kirk.credentials import CredentialsHandler
from kirk import KirkError


@pytest.fixture
def credentials(tmp_path, mocker):
    """
    Fixture to expose credentials handler.
    """
    mocker.patch('keyrings.alt.file.PlaintextKeyring.set_password')
    mocker.patch('keyrings.alt.file.PlaintextKeyring.get_password',
                 return_value="12345")
    credentials = (tmp_path / "credentials.cfg").absolute()

    yield CredentialsHandler(credentials)


def test_set_password_exception(credentials):
    """
    Test set_password method with exception
    """
    keyrings.alt.file.PlaintextKeyring.set_password.side_effect = \
        keyring.errors.KeyringError("mocked error")

    with pytest.raises(KirkError, match="mocked error"):
        credentials.set_password("jenkins.xyz.org", "kirk", "12345")


def test_get_password_exception(credentials):
    """
    Test get_password method with exception
    """
    keyrings.alt.file.PlaintextKeyring.get_password.side_effect = \
        keyring.errors.KeyringError("mocked error")

    with pytest.raises(KirkError, match="mocked error"):
        credentials.get_password("jenkins.xyz.org", "kirk")


def test_set_password(credentials):
    """
    Test set_password method
    """
    credentials.set_password("jenkins.xyz.org", "kirk", "12345")
    keyrings.alt.file.PlaintextKeyring.set_password.assert_called_with(
        "jenkins.xyz.org",
        "kirk",
        "12345"
    )


def test_get_password(credentials):
    """
    Test get_password method
    """
    password = credentials.get_password("jenkins.xyz.org", "kirk")
    keyrings.alt.file.PlaintextKeyring.get_password.assert_called_with(
        "jenkins.xyz.org",
        "kirk"
    )
    assert password == "12345"
