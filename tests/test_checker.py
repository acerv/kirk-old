"""
test checker module
"""
import os
import yaml
import jenkins
from kirk.checker import __kirk_check
from kirk.checker import JenkinsTester


def test_kirk_check(mocker):
    """
    Test JenkinsTester implementation
    """
    # build default plugins based on defaults file
    currdir = os.path.abspath(os.path.dirname(__file__))
    config_path = os.path.join(currdir, "..", "kirk", "files", "defaults.yml")
    with open(config_path) as config_data:
        def_plugins = yaml.safe_load(config_data)['kirk']['jenkins']['plugins']

    ret_plugins_info = list()
    for plugin in def_plugins:
        ret_plugins_info.append(dict(shortName=plugin['name']))

    # create data for get_job_info
    ret_job_info = {
        "lastCompletedBuild": {
            "number": 1
        }
    }

    # patch jenkins callback
    mocker.patch('jenkins.Jenkins.__init__', return_value=None)
    mocker.patch(
        'jenkins.Jenkins.get_whoami',
        return_value={
            "fullName": "admin"
        }
    )
    mocker.patch(
        'jenkins.Jenkins.get_plugins_info',
        return_value=ret_plugins_info
    )
    mocker.patch('jenkins.Jenkins.create_job')
    mocker.patch('jenkins.Jenkins.get_job_info', return_value=ret_job_info)
    mocker.patch('jenkins.Jenkins.reconfig_job')
    mocker.patch('jenkins.Jenkins.build_job')
    mocker.patch('jenkins.Jenkins.delete_job')
    mocker.patch('jenkins.Jenkins.job_exists', return_value=False)

    # run application
    args = [
        "http://localhost:8080",
        "admin",
        "password"
    ]

    __kirk_check(args)

    # check if methods are called
    jenkins.Jenkins.__init__.assert_any_call(
        "http://localhost:8080",
        "admin",
        "password")
    jenkins.Jenkins.get_whoami.assert_any_call()
    jenkins.Jenkins.get_plugins_info.assert_any_call()
    jenkins.Jenkins.create_job.assert_called()
    jenkins.Jenkins.get_job_info.assert_any_call(JenkinsTester.TEST_JOB)
    jenkins.Jenkins.reconfig_job.assert_called()
    jenkins.Jenkins.build_job.assert_called()
    jenkins.Jenkins.delete_job.assert_called()
