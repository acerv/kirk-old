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
                    parameters:
                    - name: PARAM_0
                      label: parameter zero
                      default: zero
                      show: true
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
    Test for --help option
    """
    runner = CliRunner()
    ret = runner.invoke(kirk.commands.command_kirk, ['--help'])
    assert ret.exit_code == 0


def test_kirk_list_with_credentials():
    """
    Test for "kirk list" with --credentials option
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.mkdir("projects")
        ret = runner.invoke(
            kirk.commands.command_kirk,
            [
                '--credentials',
                'my_credentials.txt',
                'list'
            ]
        )
        assert ret.exit_code == 0
        assert "credentials: my_credentials.txt" in ret.output


def test_kirk_list_with_owner():
    """
    Test for "kirk list" with --owner option
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.mkdir("projects")
        ret = runner.invoke(
            kirk.commands.command_kirk,
            [
                '--owner',
                'my_user',
                'list'
            ]
        )
        assert ret.exit_code == 0
        assert "owner: my_user" in ret.output


def test_kirk_list_with_debug():
    """
    Test for "kirk list" with --debug option
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.mkdir("projects")
        ret = runner.invoke(
            kirk.commands.command_kirk,
            [
                '--debug',
                'list'
            ]
        )
        assert ret.exit_code == 0
        assert "debugging session" in ret.output


def test_kirk_list_with_projects_folder():
    """
    Test for "kirk list" with --projects option
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.mkdir("my_projects")
        ret = runner.invoke(
            kirk.commands.command_kirk,
            [
                '--projects',
                'my_projects',
                'list'
            ]
        )
        assert ret.exit_code == 0
        assert "collected 0 jobs" in ret.output


def test_kirk_list_jobs(create_projects):
    """
    test for "kirk list --jobs" command
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        create_projects()
        ret = runner.invoke(kirk.commands.command_kirk, ['list', '--jobs'])
        assert ret.exit_code == 0
        assert 'project_0::mytest_0[PARAM_0=zero]' in ret.output
        assert 'project_0::mytest_1[PARAM_0=zero]' in ret.output
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
        assert 'project_0::mytest_0[PARAM_0=zero]' in ret.output
        assert 'project_0::mytest_1[PARAM_0=zero]' in ret.output
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


def test_kirk_search_no_jobs(create_projects):
    """
    test for "kirk show" command when no jobs are found
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        create_projects()
        ret = runner.invoke(
            kirk.commands.command_kirk,
            [
                'search', '.*this_job_doesnt_exist'
            ]
        )
        assert ret.exit_code == 1
        assert 'No jobs found' in ret.output


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


def test_kirk_run_job_with_bad_format(mocker, create_projects):
    """
    test for 'kirk run' command with bad job format string
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        create_projects()
        ret = runner.invoke(
            kirk.commands.command_kirk,
            [
                'run',
                'this_job_doesnt_exist'
            ],
        )
        assert ret.exit_code == 1
        assert "Invalid job token" in ret.output

        ret = runner.invoke(
            kirk.commands.command_kirk,
            [
                'run',
                '::this_job_doesnt_exist'
            ],
        )
        assert ret.exit_code == 1
        assert "Invalid job token" in ret.output

        ret = runner.invoke(
            kirk.commands.command_kirk,
            [
                'run',
                '[PARam=1]this_job_doesnt_exist'
            ],
        )
        assert ret.exit_code == 1
        assert "Invalid job token" in ret.output

        ret = runner.invoke(
            kirk.commands.command_kirk,
            [
                'run',
                'mytest_1[PARAM_ZERO=zero]'
            ],
        )
        assert ret.exit_code == 1
        assert "Invalid job token" in ret.output


def test_kirk_run_with_params(mocker, create_projects):
    """
    test for 'kirk run' command with single job
    """
    mocker.patch('kirk.runner.JobRunner.run')

    runner = CliRunner()
    with runner.isolated_filesystem():
        create_projects()
        ret = runner.invoke(
            kirk.commands.command_kirk,
            [
                'run',
                'project_1::mytest_1[PARAM_ZERO=zero]'
            ],
        )
        assert ret.exit_code == 0
        jobs = kirk.commands.load_jobs("projects")
        myjob = None
        for job in jobs:
            if str(job) == "project_1::mytest_1":
                myjob = job
                break

        kirk.runner.JobRunner.run.assert_called_with(
            myjob,
            user=""
        )


def test_kirk_run_multiple(mocker, create_projects):
    """
    test for 'kirk run' command with multiple jobs
    """
    mocker.patch('kirk.runner.JobRunner.run')

    runner = CliRunner()
    with runner.isolated_filesystem():
        create_projects()
        ret = runner.invoke(
            kirk.commands.command_kirk,
            [
                'run',
                'project_0::mytest_0',
                'project_0::mytest_1',
                'project_1::mytest_0',
                'project_1::mytest_1[PARAM_0=zero,PARAM_1=one]',
            ],
        )
        assert ret.exit_code == 0
        jobs = kirk.commands.load_jobs("projects")
        for job in jobs:
            kirk.runner.JobRunner.run.assert_any_call(
                job,
                user=""
            )


def test_kirk_run_with_user(mocker, create_projects):
    """
    test for 'kirk run --user' command
    """
    mocker.patch('kirk.runner.JobRunner.run')

    runner = CliRunner()
    with runner.isolated_filesystem():
        create_projects()
        ret = runner.invoke(
            kirk.commands.command_kirk,
            [
                'run',
                'project_1::mytest_1',
                '--user',
                'admin'
            ],
        )
        assert ret.exit_code == 0
        kirk.runner.JobRunner.run.assert_called_with(
            mocker.ANY,
            user="admin"
        )


def test_kirk_run_job_not_found(mocker, create_projects):
    """
    test for 'kirk run' command when job is not found
    """
    mocker.patch('kirk.runner.JobRunner.run')

    runner = CliRunner()
    with runner.isolated_filesystem():
        create_projects()
        ret = runner.invoke(
            kirk.commands.command_kirk,
            [
                'run',
                'this_job_doesnt_exist::job'
            ],
        )
        assert ret.exit_code == 1
        assert "Cannot find the following jobs" in ret.output


def test_kirk_check(mocker):
    """
    Test JenkinsTester implementation
    """
    mocker.patch('time.sleep')
    mocker.patch('kirk.checker.JenkinsTester.test_connection')
    mocker.patch('kirk.checker.JenkinsTester.test_plugins')
    mocker.patch('kirk.checker.JenkinsTester.test_job_create')
    mocker.patch('kirk.checker.JenkinsTester.test_job_config')
    mocker.patch('kirk.checker.JenkinsTester.test_job_info')
    mocker.patch('kirk.checker.JenkinsTester.test_job_build')
    mocker.patch('kirk.checker.JenkinsTester.test_job_delete')

    runner = CliRunner()
    ret = runner.invoke(
        kirk.commands.command_check,
        [
            'http://localhost:8080',
            'admin',
            'password'
        ]
    )
    assert ret.exit_code == 0

    kirk.checker.JenkinsTester.test_connection.assert_called_once()
    kirk.checker.JenkinsTester.test_plugins.assert_called_once()
    kirk.checker.JenkinsTester.test_job_create.assert_called_once()
    kirk.checker.JenkinsTester.test_job_config.assert_called_once()
    kirk.checker.JenkinsTester.test_job_info.assert_called_once()
    kirk.checker.JenkinsTester.test_job_build.assert_called_once()
    kirk.checker.JenkinsTester.test_job_delete.assert_called_once()
