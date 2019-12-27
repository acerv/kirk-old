"""
tests for checker module
"""
import os
import yaml
import pytest
import jenkins
from kirk.checker import JenkinsTester
from kirk import KirkError


@pytest.fixture
def tester(mocker):
    """
    Default jenkins tester
    """
    currdir = os.path.abspath(os.path.dirname(__file__))
    config_path = os.path.join(currdir, "..", "kirk", "files", "defaults.yml")
    with open(config_path) as config_data:
        def_plugins = yaml.safe_load(config_data)['kirk']['jenkins']['plugins']

    ret_plugins_info = list()
    for plugin in def_plugins:
        ret_plugins_info.append(dict(shortName=plugin['name']))

    mocker.patch('jenkins.Jenkins.__init__', return_value=None)
    mocker.patch('jenkins.Jenkins.get_whoami', return_value={
        "fullName": "admin"
    })
    mocker.patch(
        'jenkins.Jenkins.get_plugins_info',
        return_value=ret_plugins_info
    )
    mocker.patch('jenkins.Jenkins.create_job')
    mocker.patch('jenkins.Jenkins.reconfig_job')
    mocker.patch('jenkins.Jenkins.build_job')
    mocker.patch(
        'jenkins.Jenkins.get_job_info',
        return_value={
            "lastCompletedBuild": {
                "number": 1
            }
        }
    )
    mocker.patch('jenkins.Jenkins.delete_job')

    obj = JenkinsTester(
        "http://localhost:8080",
        "admin",
        "password"
    )

    jenkins.Jenkins.__init__.assert_any_call(
        "http://localhost:8080",
        "admin",
        "password")

    return obj


def test_connected(mocker, tester):
    """
    test_connected test
    """
    tester.test_connection()
    jenkins.Jenkins.get_whoami.assert_called_once()


def test_connected_exception(mocker, tester):
    """
    test_connected test with exception
    """
    jenkins.Jenkins.get_whoami.side_effect = \
        jenkins.JenkinsException("mocked exception")

    with pytest.raises(KirkError, match="mocked exception"):
        tester.test_connection()


def test_connected_bad_get_whoami(mocker, tester):
    """
    test_connected test with exception
    """
    jenkins.Jenkins.get_whoami.return_value = dict(fullName="jesus")
    with pytest.raises(KirkError):
        tester.test_connection()


def test_plugins(mocker, tester):
    """
    test_plugins test
    """
    tester.test_plugins()
    jenkins.Jenkins.get_plugins_info.assert_called_once()


def test_plugins_exception(mocker, tester):
    """
    test_plugins test with exception
    """
    jenkins.Jenkins.get_plugins_info.side_effect = \
        jenkins.JenkinsException("mocked exception")

    with pytest.raises(KirkError, match="mocked exception"):
        tester.test_plugins()


def test_plugins_no_plugin(mocker, tester):
    """
    test_plugins test when it doesn't find a plugin in the server
    """
    jenkins.Jenkins.get_plugins_info.return_value = []

    with pytest.raises(KirkError):
        tester.test_plugins()


def test_job_create(mocker, tester):
    """
    test_job_create test
    """
    tester.test_job_create()
    jenkins.Jenkins.create_job.assert_called_once()


def test_job_create_exception(mocker, tester):
    """
    test_job_create test with exception
    """
    jenkins.Jenkins.create_job.side_effect = \
        jenkins.JenkinsException("mocked exception")

    with pytest.raises(KirkError, match="mocked exception"):
        tester.test_job_create()


def test_job_config(mocker, tester):
    """
    test_job_config test
    """
    tester.test_job_config()
    jenkins.Jenkins.reconfig_job.assert_called_once()


def test_job_config_exception(mocker, tester):
    """
    test_job_config test with exception
    """
    jenkins.Jenkins.reconfig_job.side_effect = \
        jenkins.JenkinsException("mocked exception")

    with pytest.raises(KirkError, match="mocked exception"):
        tester.test_job_config()


def test_job_info(mocker, tester):
    """
    test_job_info test
    """
    tester.test_job_info()
    jenkins.Jenkins.get_job_info.assert_called_once()


def test_job_info_exception(mocker, tester):
    """
    test_job_info test with exception
    """
    jenkins.Jenkins.get_job_info.side_effect = \
        jenkins.JenkinsException("mocked exception")

    with pytest.raises(KirkError, match="mocked exception"):
        tester.test_job_info()


def test_job_build(mocker, tester):
    """
    test_job_build test
    """
    tester.test_job_build()
    jenkins.Jenkins.build_job.assert_called_once()


def test_job_build_exception(mocker, tester):
    """
    test_job_build test with exception
    """
    jenkins.Jenkins.build_job.side_effect = \
        jenkins.JenkinsException("mocked exception")

    with pytest.raises(KirkError, match="mocked exception"):
        tester.test_job_build()


def test_job_delete(mocker, tester):
    """
    test_job_delete test
    """
    tester.test_job_delete()
    jenkins.Jenkins.delete_job.assert_called_once()


def test_job_delete_exception(mocker, tester):
    """
    test_job_delete test with exception
    """
    jenkins.Jenkins.delete_job.side_effect = \
        jenkins.JenkinsException("mocked exception")

    with pytest.raises(KirkError, match="mocked exception"):
        tester.test_job_delete()
