"""
tokenizer module tests.
"""
import pytest
from kirk.tokenizer import JobTokenizer


class TestJobTokenizer:
    """
    Test JobTokenizer class
    """

    @pytest.fixture
    def tokenizer(self):
        """
        Fixture exposing default tokenizer.
        """
        return JobTokenizer()

    def test_encode_no_params(self, tokenizer):
        """
        Test encode method with a single parameter for one job
        """
        assert "myproject::myjob" == tokenizer.encode(
            "myproject", "myjob", dict())

    def test_encode_hide_params(self, tokenizer):
        """
        Test encode method with show_params=False
        """
        assert "myproject::myjob" == tokenizer.encode(
            "myproject", "myjob", None)

    def test_encode_single_param(self, tokenizer):
        """
        Test encode method with a single parameter for one job
        """
        assert "myproject::myjob[param0=0]" == tokenizer.encode(
            "myproject", "myjob", dict(param0="0"))

    def test_encode_multiple_params(self, tokenizer):
        """
        Test encode method with multiple parameters for one job
        """
        assert "myproject::myjob[param0=0,param1=1]" == tokenizer.encode(
            "myproject", "myjob", dict(param0="0", param1="1"))

    def test_encode_errors(self, tokenizer):
        """
        Test encode method with bad formatted parameters for one job
        """
        with pytest.raises(ValueError, match="project name is empty"):
            tokenizer.encode("", "myjob", dict())

        with pytest.raises(ValueError, match="job name is empty"):
            tokenizer.encode("myproject", "", dict())

    def test_decode_no_params(self, tokenizer):
        """
        Test decode method with no params
        """
        assert ("myproject", "myjob", dict()) == tokenizer.decode(
            "myproject::myjob")

    def test_decode_single_param(self, tokenizer):
        """
        Test decode method with a single param
        """
        assert ("myproject", "myjob", dict(param0="0")) == tokenizer.decode(
            "myproject::myjob[param0=0]")

    def test_decode_multiple_params(self, tokenizer):
        """
        Test decode method with multiple params
        """
        assert ("myproject", "myjob", dict(param0="0", param1="1")) == tokenizer.decode(
            "myproject::myjob[param0=0,param1=1]")

    def test_decode_errors(self, tokenizer):
        """
        Test dencode method with bad formatted parameters for one job
        """
        with pytest.raises(ValueError, match="token is empty"):
            tokenizer.decode("")

    def test_decode_no_match(self, tokenizer):
        """
        Test dencode method when a bad token is given
        """
        assert tokenizer.decode("myproject:") == None

    def test_decode_params_spaces(self, tokenizer):
        """
        Test dencode method when parameters are splitted by spaces
        """
        assert ("myproject", "myjob", dict(param0="0", param1="1")) == tokenizer.decode(
            "myproject::myjob[param0=0,      param1=1]")
