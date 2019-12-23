"""
Test kirk command defined in the cmd module
"""
import os
import pytest
from click.testing import CliRunner
import kirk.commands
import kirk.runner


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


def test_kirk_help():
    """
    Check for --help option
    """
    runner = CliRunner()
    ret = runner.invoke(kirk.commands.command_kirk, '--help')
    assert ret.exit_code == 0


def test_kirk_list_jobs(create_projects):
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


def test_kirk_list_projects(create_projects):
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


def test_kirk_search(create_projects):
    """
    test for "kirk show" command
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        create_projects()
        ret = runner.invoke(
            kirk.commands.command_kirk,
            [
                'search', '.*project_1'
            ]
        )
        assert ret.exit_code == 0
        assert 'project_0::mytest_0' not in ret.output
        assert 'project_0::mytest_1' not in ret.output
        assert 'project_1::mytest_0' in ret.output
        assert 'project_1::mytest_1[PARAM_0=zero]' in ret.output


def test_kirk_credential(mocker):
    """
    test for "kirk credential" command
    """
    mocker.patch('kirk.credentials.CredentialsHandler.set_password')

    runner = CliRunner()
    with runner.isolated_filesystem():
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

        kirk.credentials.CredentialsHandler.set_password.assert_any_call(
            "http://localhost:8080",
            "admin",
            "password"
        )


def test_kirk_run(mocker, create_projects):
    """
    test for 'kirk run' command
    """
    mocker.patch('kirk.runner.JobRunner.run')

    runner = CliRunner()
    with runner.isolated_filesystem():
        create_projects()
        ret = runner.invoke(
            kirk.commands.command_kirk,
            [
                'run',
                'project_1::mytest_0',
                '-u',
                'admin',
                '--change-id',
                'develop'
            ],
        )
        assert ret.exit_code == 0
        jobs = kirk.commands.load_jobs("projects")
        myjob = None
        for job in jobs:
            if str(job) == "project_1::mytest_0":
                myjob = job
                break
        kirk.runner.JobRunner.run.assert_called_with(
            myjob,
            "admin",
            "develop"
        )


def test_kirk_check(mocker):
    """
    Test JenkinsTester implementation
    """
    # build default plugins based on defaults file
    mocker.patch('kirk.checker.JenkinsTester.test_connection')
    mocker.patch('kirk.checker.JenkinsTester.test_plugins')
    mocker.patch('kirk.checker.JenkinsTester.test_job_create')
    mocker.patch('kirk.checker.JenkinsTester.test_job_config')
    mocker.patch('kirk.checker.JenkinsTester.test_job_info')
    mocker.patch('kirk.checker.JenkinsTester.test_job_build')
    mocker.patch('kirk.checker.JenkinsTester.test_job_delete')

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
    kirk.checker.JenkinsTester.test_connection.assert_called_once()
    kirk.checker.JenkinsTester.test_plugins.assert_called_once()
    kirk.checker.JenkinsTester.test_job_create.assert_called_once()
    kirk.checker.JenkinsTester.test_job_config.assert_called_once()
    kirk.checker.JenkinsTester.test_job_info.assert_called_once()
    kirk.checker.JenkinsTester.test_job_build.assert_called_once()
    kirk.checker.JenkinsTester.test_job_delete.assert_called_once()
