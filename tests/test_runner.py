"""
runner module tests.
"""
import jenkins
import kirk.loader
from kirk.runner import Runner

MOCKED = True


def test_runner_run(tmp_path, mocker):
    """
    Test Runner::run method
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
        jobs:
            - name: test_name0
    """)
    if MOCKED:
        # pylint: disable=no-member
        mocker.patch('jenkins.Jenkins.__init__', return_value=None)
        mocker.patch('jenkins.Jenkins.get_job_config')
        mocker.patch('jenkins.Jenkins.create_job')  # cannot test xml
        mocker.patch('jenkins.Jenkins.reconfig_job')  # cannot test xml
        mocker.patch('jenkins.Jenkins.build_job')

        # test with existing jobs
        mocker.patch('jenkins.Jenkins.job_exists', return_value=True)

    projects = kirk.loader.load(str(tmp_path))

    runner = Runner('admin', '11ae01e3bffee6c3e16f9034630950fbf1', projects)
    runner.run_as_owner('project0', 'test_name0')
    runner.run_as_developer('project0', 'test_name0')

    if MOCKED:
        # check if jobs are reconfigured
        jenkins.Jenkins.reconfig_job.assert_called()
        jenkins.Jenkins.reconfig_job.assert_called()

        jenkins.Jenkins.__init__.assert_any_call(
            "http://localhost:8080",
            "admin",
            "11ae01e3bffee6c3e16f9034630950fbf1")
        jenkins.Jenkins.job_exists.assert_any_call("myProject/seed")
        jenkins.Jenkins.job_exists.assert_any_call("myProject/dev")
        jenkins.Jenkins.job_exists.assert_any_call("myProject/dev/admin")
        jenkins.Jenkins.job_exists.assert_any_call("myProject/dev/admin/seed")
        jenkins.Jenkins.build_job.assert_any_call(
            "myProject/seed",
            parameters=dict())
        jenkins.Jenkins.build_job.assert_any_call(
            "myProject/dev/admin/seed",
            parameters=dict())

        # test with jobs that doesn't exist
        mocker.patch('jenkins.Jenkins.job_exists', return_value=False)

    runner.run_as_owner('project0', 'test_name0')
    runner.run_as_developer('project0', 'test_name0')

    if MOCKED:
        jenkins.Jenkins.create_job.assert_called()
        jenkins.Jenkins.create_job.assert_called()
