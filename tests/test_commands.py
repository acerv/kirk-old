"""
Test kirk command defined in the cmd module
"""
import os
import yaml
import pytest
import jenkins
from click.testing import CliRunner
import kirk.commands


@pytest.fixture
def create_projects():
    """
    Fixture to create projects folder.
    """
    def _callback():
        os.mkdir("projects")
        with open("projects/project0.yml", "w+") as projfile:
            projfile.write("""
                name: project_0
                description: my project 0
                author: pippo
                year: 3010
                version: 1.0
                location: myProject_0
                defaults:
                    server: http://localhost:8080
                jobs:
                    - name: mytest_0
                    - name: mytest_1
            """)
        with open("projects/project1.yml", "w+") as projfile:
            projfile.write("""
                name: project_1
                description: my project 1
                author: pippo
                year: 3010
                version: 1.0
                location: myProject_1
                defaults:
                    server: http://localhost:8080
                jobs:
                    - name: mytest_0
                    - name: mytest_1
                      parameters:
                      - name: PARAM_0
                        label: parameter zero
                        default: zero
                        show: true
                      - name: PARAM_1
                        label: parameter one
                        default: one
                        show: false
            """)
    return _callback


def test_help():
    """
    Check for --help option
    """
    runner = CliRunner()
    ret = runner.invoke(kirk.commands.command_kirk, '--help')
    assert ret.exit_code == 0


def test_list_jobs(create_projects):
    """
    test for "kirk list --jobs" command
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        create_projects()
        ret = runner.invoke(kirk.commands.command_kirk, ['list', '--jobs'])
        assert ret.exit_code == 0
        assert 'project_0::mytest_0' in ret.output
        assert 'project_0::mytest_1' in ret.output
        assert 'project_1::mytest_0' in ret.output
        assert 'project_1::mytest_1[PARAM_0=zero]' in ret.output


def test_list_projects(create_projects):
    """
    test for "kirk list" command
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        create_projects()
        ret = runner.invoke(kirk.commands.command_kirk, ['list'])
        assert ret.exit_code == 0
        assert 'project_0::mytest_0' in ret.output
        assert 'project_0::mytest_1' in ret.output
        assert 'project_1::mytest_0' in ret.output
        assert 'project_1::mytest_1[PARAM_0=zero]' in ret.output


def test_search(create_projects):
    """
    test for "kirk show" command
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        create_projects()
        ret = runner.invoke(kirk.commands.command_kirk,
                            ['search', '.*project_1'])
        assert ret.exit_code == 0
        assert 'project_0::mytest_0' not in ret.output
        assert 'project_0::mytest_1' not in ret.output
        assert 'project_1::mytest_0' in ret.output
        assert 'project_1::mytest_1[PARAM_0=zero]' in ret.output


def test_credential(create_projects):
    """
    test for "kirk credential" command
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        create_projects()
        ret = runner.invoke(
            kirk.commands.command_credential,
            [
                'http://localhost:8080',
                'admin',
                '-c',
                'credentials.txt'
            ],
            input="password"
        )
        assert ret.exit_code == 0
        assert os.path.isfile("credentials.txt")


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
    runner = CliRunner()
    runner.invoke(
        kirk.commands.command_check,
        [
            'http://localhost:8080',
            'admin',
            'password'
        ]
    )

    # check if methods are called
    jenkins.Jenkins.__init__.assert_any_call(
        "http://localhost:8080",
        "admin",
        "password")
    jenkins.Jenkins.get_whoami.assert_any_call()
    jenkins.Jenkins.get_plugins_info.assert_any_call()
    jenkins.Jenkins.create_job.assert_called()
    jenkins.Jenkins.get_job_info.assert_any_call(
        kirk.checker.JenkinsTester.TEST_JOB)
    jenkins.Jenkins.reconfig_job.assert_called()
    jenkins.Jenkins.build_job.assert_called()
    jenkins.Jenkins.delete_job.assert_called()
