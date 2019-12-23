"""
runner module tests.
"""
import pytest
import jenkins
import kirk.utils
import kirk.credentials
from kirk.runner import JobRunner
from kirk.credentials import CredentialsHandler
from kirk import __version__

MOCKED = True


def test_runner_run_invalid_args():
    """
    Test run method with invalid args
    """
    runner = JobRunner(None)
    with pytest.raises(ValueError, match="job is empty"):
        runner.run(None)
    with pytest.raises(ValueError, match="dev_folder is empty"):
        runner.run("abc", dev_folder=None)


def test_runner_run(tmp_path, mocker):
    """
    Test run method
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

    # create credentials file
    credentials = CredentialsHandler(tmp_path / "credentials.cfg")
    credentials.set_password(
        "http://localhost:8080",
        "kirk",
        "6336b50de5944aca821aa8131360886b")

    # pylint: disable=no-member
    if MOCKED:
        mocker.patch('jenkins.Jenkins.__init__', return_value=None)
        mocker.patch('jenkins.Jenkins.get_job_config')
        mocker.patch('jenkins.Jenkins.create_job')  # cannot test xml
        mocker.patch('jenkins.Jenkins.reconfig_job')  # cannot test xml
        mocker.patch('jenkins.Jenkins.build_job')
        mocker.patch('jenkins.Jenkins.get_job_info')

        # test with existing jobs
        mocker.patch('jenkins.Jenkins.job_exists', return_value=True)

    # test with jobs that does exist
    runner = JobRunner(credentials)
    runner.run(jobs[0])
    runner.run(jobs[0], user="admin")
    runner.run(jobs[0], user="admin", change_id="test")

    if MOCKED:
        jenkins.Jenkins.reconfig_job.assert_called()
        jenkins.Jenkins.reconfig_job.assert_called()

        jenkins.Jenkins.__init__.assert_any_call(
            "http://localhost:8080",
            "kirk",
            "6336b50de5944aca821aa8131360886b")
        jenkins.Jenkins.job_exists.assert_any_call("myProject/test_name0")
        jenkins.Jenkins.job_exists.assert_any_call("myProject/dev")
        jenkins.Jenkins.job_exists.assert_any_call("myProject/dev/admin")
        jenkins.Jenkins.job_exists.assert_any_call(
            "myProject/dev/admin/test_name0")
        jenkins.Jenkins.build_job.assert_any_call(
            "myProject/test_name0",
            parameters=dict(
                KIRK_VERSION=__version__,
                MY_PARAM='ABC'
            ))
        jenkins.Jenkins.get_job_info.assert_any_call(
            "myProject/test_name0")
        jenkins.Jenkins.build_job.assert_any_call(
            "myProject/dev/admin/test_name0",
            parameters=dict(
                KIRK_VERSION=__version__,
                MY_PARAM='ABC'
            ))
        jenkins.Jenkins.get_job_info.assert_any_call(
            "myProject/dev/admin/test_name0")

    # test with jobs that does NOT exist
    if MOCKED:
        mocker.patch('jenkins.Jenkins.job_exists', return_value=False)

    runner.run(jobs[0])

    if MOCKED:
        jenkins.Jenkins.create_job.assert_called()
