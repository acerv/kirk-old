"""
Test credentials module
"""
import os
import pytest
from kirk.credentials import PlaintextCredentials


class TestPlaintextCredentials:
    """
    Test PlaintextCredentials class
    """

    _credentials = ""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """
        Test setup
        """
        self._credentials = tmp_path / "credentials.cfg"

    @pytest.fixture(autouse=True)
    def teardown(self, tmp_path):
        """
        Test teardown
        """
        if os.path.isfile(self._credentials):
            os.remove(self._credentials)

    @pytest.fixture
    def credentials(self):
        """
        Fixture to expose credentials handler.
        """
        return PlaintextCredentials(self._credentials)

    def test_password_storage(self, credentials):
        """
        Save and read a password and check if it matches.
        """
        credentials.set_password("jenkins.xyz.org", "kirk", "12345")
        assert os.path.isfile(self._credentials)

        password = credentials.get_password("jenkins.xyz.org", "kirk")
        assert password == "12345"
