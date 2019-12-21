"""
Test kirk command defined in the cmd module
"""
import os
import pytest


@pytest.fixture
def create_projects(tmp_path):
    """
    Fixture to create projects folder.
    """
    def _callback():
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        project_file = projects_dir / "project0.yml"
        project_file.write_text("""
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
        project_file = projects_dir / "project1.yml"
        project_file.write_text("""
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
        return tmp_path
    yield _callback


def test_help(script_runner):
    """
    Check for --help option
    """
    ret = script_runner.run('kirk', '--help')
    assert ret.success


def test_show_jobs(script_runner, create_projects):
    """
    test for "kirk show --jobs" command
    """
    tmp_path = create_projects()
    ret = script_runner.run(
        'kirk',
        'show',
        '--jobs',
        cwd=tmp_path.absolute())
    assert ret.success
    assert 'project_0::mytest_0' in ret.stdout
    assert 'project_0::mytest_1' in ret.stdout
    assert 'project_1::mytest_0' in ret.stdout
    assert 'project_1::mytest_1[PARAM_0=zero]' in ret.stdout


def test_show_projects(script_runner, create_projects):
    """
    test for "kirk show" command
    """
    tmp_path = create_projects()
    ret = script_runner.run(
        'kirk',
        'show',
        cwd=tmp_path.absolute())
    assert ret.success
    assert 'project_0::mytest_0' in ret.stdout
    assert 'project_0::mytest_1' in ret.stdout
    assert 'project_1::mytest_0' in ret.stdout
    assert 'project_1::mytest_1[PARAM_0=zero]' in ret.stdout


def test_search(script_runner, create_projects):
    """
    test for "kirk show" command
    """
    tmp_path = create_projects()
    ret = script_runner.run(
        'kirk',
        'search',
        '.*project_1',
        cwd=tmp_path.absolute())
    assert ret.success
    assert 'project_0::mytest_0' not in ret.stdout
    assert 'project_0::mytest_1' not in ret.stdout
    assert 'project_1::mytest_0' in ret.stdout
    assert 'project_1::mytest_1[PARAM_0=zero]' in ret.stdout


def test_credential(script_runner, tmp_path):
    """
    test for "kirk credential" command
    """
    ret = script_runner.run(
        'kirk',
        'credential',
        'http://localhost:8080',
        'admin',
        'password',
        cwd=tmp_path.absolute())
    credentials_file = tmp_path / "credentials.cfg"
    assert os.path.isfile(credentials_file.absolute())
