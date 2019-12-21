"""
Test kirk command defined in the cmd module
"""
import pytest


def test_help(script_runner):
    """
    Check for --help option
    """
    ret = script_runner.run('kirk', '--help')
    assert ret.success
