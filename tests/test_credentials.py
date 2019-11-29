"""
Test credentials module
"""
import os
import pytest
import kirk.credentials


class TestCredentials:
    """
    Test credentials module
    """

    credentials = ""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        self.credentials = tmp_path / "credentials.cfg"

    @pytest.fixture(autouse=True)
    def teardown(self, tmp_path):
        if os.path.isfile(self.credentials):
            os.remove(self.credentials)

    def test_password_storage(self):
        """
        Save and read a password and check if it matches.
        """
        kirk.credentials.set_password(
            self.credentials, "jenkins.xyz.org", "kirk", "12345")
        assert os.path.isfile(self.credentials)

        password = kirk.credentials.get_password(
            self.credentials, "jenkins.xyz.org", "kirk")
        assert password == "12345"
