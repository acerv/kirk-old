"""
Test kirk command defined in the cmd module
"""
import os
import pytest
from click.testing import CliRunner
import kirk.cmd


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
    ret = runner.invoke(kirk.cmd.client, '--help')
    assert ret.exit_code == 0


def test_show_jobs(create_projects):
    """
    test for "kirk show --jobs" command
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        create_projects()
        ret = runner.invoke(kirk.cmd.client, ['show', '--jobs'])
        assert ret.exit_code == 0
        assert 'project_0::mytest_0' in ret.output
        assert 'project_0::mytest_1' in ret.output
        assert 'project_1::mytest_0' in ret.output
        assert 'project_1::mytest_1[PARAM_0=zero]' in ret.output


def test_show_projects(create_projects):
    """
    test for "kirk show" command
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        create_projects()
        ret = runner.invoke(kirk.cmd.client, ['show'])
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
        ret = runner.invoke(kirk.cmd.client, ['search', '.*project_1'])
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
            kirk.cmd.client,
            [
                'credential',
                'http://localhost:8080',
                'admin',
                'password'
            ]
        )
        assert ret.exit_code == 0
        assert os.path.isfile("credentials.cfg")
