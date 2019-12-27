"""
runner module tests.
"""
import pytest
import jenkins
import kirk.utils
import kirk.credentials
from kirk.runner import JobRunner
from kirk import __version__
from kirk import KirkError


@pytest.fixture
def runner(mocker):
    """
    JobRunner instance
    """
    # pylint: disable=no-member
    mocker.patch('jenkins.Jenkins.__init__', return_value=None)
    mocker.patch('jenkins.Jenkins.get_job_config')
    mocker.patch('jenkins.Jenkins.create_job')  # cannot test xml
    mocker.patch('jenkins.Jenkins.reconfig_job')  # cannot test xml
    mocker.patch('jenkins.Jenkins.build_job')
    mocker.patch('jenkins.Jenkins.get_job_info')
    mocker.patch('jenkins.Jenkins.job_exists', return_value=False)

    # mock credentials handler
    mocker.patch(
        'kirk.credentials.CredentialsHandler.get_password',
        return_value="password")

    credentials = kirk.credentials.CredentialsHandler("credentials.cfg")

    # test with jobs that does exist
    runner = JobRunner(credentials)
    return runner


@pytest.fixture
def jobs(tmp_path):
    """
    Jobs to run
    """
    project_file0 = tmp_path / "project0.yml"
    project_file0.write_text("""
        name: project0
        description: my project 0
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: http://localhost:8080
            scm:
                git:
                    url: https://github.com/acerv/marvin.git
        jobs:
            - name: test_name0
              pipeline: pipeline.groovy
              parameters:
                - name: MY_PARAM
                  label: Parameter XYZ
                  default: ABC
                  show: true
    """)
    jobs = kirk.utils.get_jobs_from_folder(str(tmp_path))
    return jobs


def test_runner_run_invalid_args():
    """
    Test run method with invalid args
    """
    runner = JobRunner(None)
    with pytest.raises(ValueError, match="job is empty"):
        runner.run(None)
    with pytest.raises(ValueError, match="dev_folder is empty"):
        runner.run("abc", dev_folder=None)


def test_runner_run_exception(runner, jobs):
    """
    Test run method raising exception
    """
    jenkins.Jenkins.build_job.side_effect = \
        jenkins.JenkinsException("mocked exception")

    with pytest.raises(KirkError, match="mocked exception"):
        runner.run(jobs[0])


def test_runner_run(runner, jobs):
    """
    Test run method without parameters
    """
    runner.run(jobs[0])

    jenkins.Jenkins.__init__.assert_called_with(
        "http://localhost:8080",
        "kirk",
        "password")
    jenkins.Jenkins.build_job.assert_called_with(
        "myProject/test_name0",
        parameters=dict(
            KIRK_VERSION=__version__,
            MY_PARAM='ABC'
        ))
    jenkins.Jenkins.get_job_info.assert_called_with(
        "myProject/test_name0")


def test_runner_run_job_exists(mocker, runner, jobs):
    """
    Test run method with a job that already exists
    """
    mocker.patch('jenkins.Jenkins.job_exists', return_value=True)

    runner.run(jobs[0])

    jenkins.Jenkins.__init__.assert_called_with(
        "http://localhost:8080",
        "kirk",
        "password")
    jenkins.Jenkins.job_exists.assert_called_with("myProject/test_name0")
    jenkins.Jenkins.reconfig_job.assert_called()
    jenkins.Jenkins.build_job.assert_called_with(
        "myProject/test_name0",
        parameters=dict(
            KIRK_VERSION=__version__,
            MY_PARAM='ABC'
        ))
    jenkins.Jenkins.get_job_info.assert_called_with(
        "myProject/test_name0")


def test_runner_run_with_username(runner, jobs):
    """
    Test run method with username
    """
    runner.run(jobs[0], user="admin")

    jenkins.Jenkins.__init__.assert_called_with(
        "http://localhost:8080",
        "kirk",
        "password")
    jenkins.Jenkins.job_exists.assert_any_call("myProject/dev")
    jenkins.Jenkins.job_exists.assert_any_call("myProject/dev/admin")
    jenkins.Jenkins.job_exists.assert_any_call(
        "myProject/dev/admin/test_name0")
    jenkins.Jenkins.create_job.assert_called()
    jenkins.Jenkins.build_job.assert_called_with(
        "myProject/dev/admin/test_name0",
        parameters=dict(
            KIRK_VERSION=__version__,
            MY_PARAM='ABC'
        ))
    jenkins.Jenkins.get_job_info.assert_called_with(
        "myProject/dev/admin/test_name0")


def test_runner_run_with_dev_folder(runner, jobs):
    """
    Test run method with development folder
    """
    runner.run(jobs[0], user="admin", dev_folder="my_dev")

    jenkins.Jenkins.__init__.assert_called_with(
        "http://localhost:8080",
        "kirk",
        "password")
    jenkins.Jenkins.job_exists.assert_any_call("myProject/my_dev")
    jenkins.Jenkins.job_exists.assert_any_call("myProject/my_dev/admin")
    jenkins.Jenkins.job_exists.assert_any_call(
        "myProject/my_dev/admin/test_name0")
    jenkins.Jenkins.create_job.assert_called()
    jenkins.Jenkins.build_job.assert_called_with(
        "myProject/my_dev/admin/test_name0",
        parameters=dict(
            KIRK_VERSION=__version__,
            MY_PARAM='ABC'
        ))
    jenkins.Jenkins.get_job_info.assert_called_with(
        "myProject/my_dev/admin/test_name0")


def test_runner_run_with_change(runner, jobs):
    """
    Test run method with change_id parameter
    """
    runner.run(jobs[0], change_id="123456")

    jenkins.Jenkins.__init__.assert_called_with(
        "http://localhost:8080",
        "kirk",
        "password")
    jenkins.Jenkins.build_job.assert_called_with(
        "myProject/test_name0",
        parameters=dict(
            KIRK_VERSION=__version__,
            MY_PARAM='ABC'
        ))
    jenkins.Jenkins.get_job_info.assert_called_with(
        "myProject/test_name0")


def test_runner_run_with_parameter(runner, jobs):
    """
    Test run method with change_id parameter
    """
    jobs[0].parameters[0].value = "DEF"

    runner.run(jobs[0])

    jenkins.Jenkins.__init__.assert_called_with(
        "http://localhost:8080",
        "kirk",
        "password")
    jenkins.Jenkins.build_job.assert_called_with(
        "myProject/test_name0",
        parameters=dict(
            KIRK_VERSION=__version__,
            MY_PARAM='DEF'
        ))
    jenkins.Jenkins.get_job_info.assert_called_with(
        "myProject/test_name0")
