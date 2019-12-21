"""
Tests for yaml_env module.
"""
import os
import pytest
import kirk.yaml_env as yaml_env
from kirk import KirkError


def test_load_invalid_args(tmp_path):
    """
    Test load method with invalid args.
    """
    with pytest.raises(ValueError):
        yaml_env.load(None)
    with pytest.raises(ValueError):
        yaml_env.load("file.yml", None)
    with pytest.raises(ValueError):
        yaml_env.load("file.yml")
    with pytest.raises(KirkError):
        myfile = tmp_path / "myfile.txt"
        myfile.write_text("abc")
        yaml_env.load(str(myfile.absolute()))


def test_load(tmp_path):
    """
    Test load method with environment variables.
    """
    myfile = tmp_path / "myfile.yml"
    myfile.write_text("""
        name: !ENV ${__MY_VAR__}
    """)
    os.environ['__MY_VAR__'] = "hello"
    myfile_dict = yaml_env.load(str(myfile.absolute()))

    assert myfile_dict['name'] == "hello"


def test_load_invalid_definition(tmp_path):
    """
    Test load method with invalid environment variables definition.
    """
    myfile = tmp_path / "myfile.yml"
    myfile.write_text("""
        name0: !ENV ${__MY_VAR__
        name1: !ENV __MY_VAR__
    """)
    os.environ['__MY_VAR__'] = "hello"
    myfile_dict = yaml_env.load(str(myfile.absolute()))

    assert myfile_dict['name0'] == "${__MY_VAR__"
    assert myfile_dict['name1'] == "__MY_VAR__"
    assert myfile_dict['name1'] == "__MY_VAR__"
