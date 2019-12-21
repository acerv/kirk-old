"""
config module tests.
"""
import os
import pytest
from kirk import KirkError
from kirk.project import Project


def test_project_empty_path():
    """
    Test if project raises an exception when no path is given
    """
    proj = Project()
    with pytest.raises(ValueError):
        proj.load(None)


def test_project_missing_defaults(tmp_path):
    """
    Test project file when defaults is not defined
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        
        jobs:
            - name: myJob
    """)
    proj = Project()
    with pytest.raises(KirkError):
        proj.load(str(project_file.absolute()))


def test_project_missing_jobs(tmp_path):
    """
    Test project file when jobs is not defined
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: myserver.com
    """)
    proj = Project()
    with pytest.raises(KirkError):
        proj.load(str(project_file.absolute()))


def test_project_not_supported_file(tmp_path):
    """
    Test project file when it's not supported
    """
    project_file = tmp_path / "project.txt"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: myserver.com
        jobs:
            - name: Test_mytest
    """)
    proj = Project()
    with pytest.raises(KirkError, match="'.txt' file type is not supported"):
        proj.load(str(project_file.absolute()))


def test_project_base(tmp_path):
    """
    Test basic project file informations.
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: myserver.com
        jobs:
            - name: Test_mytest
              pipeline: pipeline.groovy
    """)
    proj = Project()
    proj.load(str(project_file.absolute()))

    assert proj.name == "project"
    assert proj.description == "my project"
    assert proj.author == "pippo"
    assert proj.year == 3010
    assert proj.version == 1.0
    assert proj.location == "myProject"

    jobs = proj.jobs
    assert len(jobs) == 1
    assert jobs[0].name == "Test_mytest"
    assert jobs[0].server == "myserver.com"
    assert jobs[0].pipeline == "pipeline.groovy"
    assert jobs[0].project == proj


def test_project_job_str(tmp_path):
    """
    Test job string rapresentation.
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: myserver.com
        jobs:
            - name: Test_mytest
              pipeline: pipeline.groovy
              parameters:
                - name: JK_TEST_0
                  label: Test name 0
                  default: test_something_0
                  show: false
                - name: JK_TEST_1
                  label: Test name 1
                  default: test_something_1
                  show: false
    """)
    proj = Project()
    proj.load(str(project_file.absolute()))

    jobs = proj.jobs
    assert len(jobs) == 1
    assert str(jobs[0]) == "project::Test_mytest"
    assert repr(jobs[0]) == "project::Test_mytest" \
        "[JK_TEST_0=test_something_0,JK_TEST_1=test_something_1]"


def test_project_multiple_jobs(tmp_path):
    """
    Test project file with multiple jobs.
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: myserver.com
        jobs:
            - name: test_seed0
              pipeline: pipeline.groovy
            - name: test_seed1
              pipeline: pipeline.groovy
            - name: test_seed2
              pipeline: pipeline.groovy
    """)
    proj = Project()
    proj.load(str(project_file.absolute()))

    jobs = proj.jobs
    assert len(jobs) == 3
    for i in range(0, 3):
        assert jobs[i].server == "myserver.com"
        assert jobs[i].name == "test_seed%d" % i
        assert jobs[i].pipeline == "pipeline.groovy"
        assert len(jobs[i].parameters) == 0


def test_project_jobs_conflict(tmp_path):
    """
    Test project file with multiple jobs with the same name.
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        defaults:
            server: myserver.com
        jobs:
            - name: test_seed0
              pipeline: pipeline.groovy
            - name: test_seed0
              pipeline: pipeline.groovy
    """)
    proj = Project()
    with pytest.raises(KirkError):
        proj.load(str(project_file.absolute()))


def test_project_server_override(tmp_path):
    """
    Test project file with server overrride.
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: myserver.com
        jobs:
            - name: test_seed1
              server: myserver2.com
              pipeline: pipeline.groovy
    """)
    proj = Project()
    proj.load(str(project_file.absolute()))

    assert proj.jobs[0].server == "myserver2.com"


def test_project_param_value(tmp_path):
    """
    Test when setting parameter value.
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: myserver.com
        jobs:
            - name: test_name0
              pipeline: pipeline.groovy
              parameters:
                - name: JK_TEST_0
                  label: Test name 0
                  default: test_something_0
                  show: false
    """)
    proj = Project()
    proj.load(str(project_file.absolute()))

    jobs = proj.jobs
    assert len(jobs[0].parameters) == 1
    assert jobs[0].parameters[0].name == "JK_TEST_0"
    assert jobs[0].parameters[0].label == "Test name 0"
    assert jobs[0].parameters[0].default == "test_something_0"
    assert jobs[0].parameters[0].show == False
    assert jobs[0].parameters[0].value == "test_something_0"
    assert str(jobs[0].parameters[0]) == "JK_TEST_0=test_something_0"

    # check assignment
    jobs[0].parameters[0].value = "test"
    assert jobs[0].parameters[0].value == "test"


def test_project_parameters(tmp_path):
    """
    Test project file with job parameters.
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: myserver.com
        jobs:
            - name: test_name0
              pipeline: pipeline.groovy
              parameters:
                - name: JK_TEST_0
                  label: Test name 0
                  default: test_something_0
                  show: false
                - name: JK_TEST_1
                  label: Test name 1
                  default: test_something_1
                  show: false
                - name: JK_TEST_2
                  label: Test name 2
                  default: test_something_2
                  show: false
    """)
    proj = Project()
    proj.load(str(project_file.absolute()))

    jobs = proj.jobs
    assert len(jobs[0].parameters) == 3
    for i in range(0, 3):
        assert jobs[0].parameters[i].name == "JK_TEST_%d" % i
        assert jobs[0].parameters[i].label == "Test name %d" % i
        assert jobs[0].parameters[i].default == "test_something_%d" % i
        assert jobs[0].parameters[i].show == False


def test_project_parameters_equals(tmp_path):
    """
    Test project file with job parameters with the same name.
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: myserver.com
            parameters:
              - name: JK_TEST_0
                label: Test name 0
                default: test_something_0
                show: false
        jobs:
            - name: test_name0
              pipeline: pipeline.groovy
              parameters:
                - name: JK_TEST_0
                  label: Test name 1
                  default: test_something_1
                  show: true
    """)
    proj = Project()
    proj.load(str(project_file.absolute()))

    jobs = proj.jobs
    assert len(jobs[0].parameters) == 1
    assert jobs[0].parameters[0].name == "JK_TEST_0"
    assert jobs[0].parameters[0].label == "Test name 1"
    assert jobs[0].parameters[0].default == "test_something_1"
    assert jobs[0].parameters[0].show == True
    assert jobs[0].parameters[0].value == "test_something_1"


def test_project_override_parameter(tmp_path):
    """
    Test project file overriding job parameters.
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: myserver.com
            parameters:
                - name: JK_TEST_0
                  label: Test name 0
                  default: test_something_0
                  show: false
        jobs:
            - name: test_name0
              pipeline: pipeline.groovy
              parameters:
                - name: JK_TEST_0
                  label: Test name 0
                  default: test_something_1
                  show: true
    """)
    proj = Project()
    proj.load(str(project_file.absolute()))

    jobs = proj.jobs
    assert len(jobs[0].parameters) == 1
    assert jobs[0].parameters[0].name == "JK_TEST_0"
    assert jobs[0].parameters[0].label == "Test name 0"
    assert jobs[0].parameters[0].default == "test_something_1"
    assert jobs[0].parameters[0].show == True


def test_project_default_parameter(tmp_path):
    """
    Test project file overriding job parameters.
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: myserver.com
            parameters:
                - name: JK_TEST_0
                  label: Test name 0
                  default: test_something_0
                  show: false
        jobs:
            - name: test_name0
              pipeline: pipeline.groovy
    """)
    proj = Project()
    proj.load(str(project_file.absolute()))

    jobs = proj.jobs
    assert len(jobs[0].parameters) == 1
    assert jobs[0].parameters[0].name == "JK_TEST_0"
    assert jobs[0].parameters[0].label == "Test name 0"
    assert jobs[0].parameters[0].default == "test_something_0"
    assert jobs[0].parameters[0].show == False


def test_project_jobs_dependences(tmp_path):
    """
    Test project file having jobs dependences.
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: myserver.com
        jobs:
            - name: test_name0
              pipeline: pipeline.groovy
            - name: test_name1
              pipeline: pipeline.groovy
              depends:
                - test_name0
            - name: test_name2
              pipeline: pipeline.groovy
              depends:
                - test_name0
                - test_name1
    """)
    proj = Project()
    proj.load(str(project_file.absolute()))

    jobs = proj.jobs
    assert len(jobs) == 3
    assert jobs[0].dependences == []
    assert jobs[1].dependences == ["test_name0"]
    assert jobs[2].dependences == ["test_name0", "test_name1"]


def test_project_scm_git(tmp_path):
    """
    Test project file defining git scm
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: myserver.com
            scm:
                git:
                    url: myurl.com/repo.git
                    checkout: development
                    credential: fbf1e43a-3442-455e-9c7f-31421a122370
        jobs:
            - name: test_seed1
              pipeline: pipeline.groovy
    """)
    proj = Project()
    proj.load(str(project_file.absolute()))

    assert proj.jobs[0].scm["git"]["url"] == "myurl.com/repo.git"
    assert proj.jobs[0].scm["git"]["checkout"] == "development"
    assert proj.jobs[0].scm["git"]["credential"] == "fbf1e43a-3442-455e-9c7f-31421a122370"


def test_project_scm_p4(tmp_path):
    """
    Test project file defining perforce scm
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: myserver.com
            scm:
                perforce:
                    stream: //depot/main
                    changelist: 1001
                    workspace: depot_main_workspace
                    credential: fbf1e43a-3442-455e-9c7f-31421a122370
        jobs:
            - name: test_seed1
              pipeline: pipeline.groovy
    """)
    proj = Project()
    proj.load(str(project_file.absolute()))

    assert proj.jobs[0].scm["perforce"]["stream"] == "//depot/main"
    assert proj.jobs[0].scm["perforce"]["changelist"] == 1001
    assert proj.jobs[0].scm["perforce"]["workspace"] == "depot_main_workspace"
    assert proj.jobs[0].scm["perforce"]["credential"] == "fbf1e43a-3442-455e-9c7f-31421a122370"


def test_project_scm_none(tmp_path):
    """
    Test project file defining perforce scm
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: myserver.com
            scm:
                none:
                    script: node { println "hello world" }
                    sandbox: false
        jobs:
            - name: test_seed1
    """)
    proj = Project()
    proj.load(str(project_file.absolute()))

    assert proj.jobs[0].scm["none"]["script"] == 'node { println "hello world" }'
    assert proj.jobs[0].scm["none"]["sandbox"] == False


def test_project_env_var(tmp_path):
    """
    Test project file with environment variables
    """
    project_file = tmp_path / "project.yml"
    project_file.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: !ENV ${LOCATION}
        defaults:
            server: myserver.com
            scm:
                perforce:
                    stream: //depot/main
                    changelist: 1001
                    workspace: depot_main_${NODE}_${JOBNAME}
                    credential: fbf1e43a-3442-455e-9c7f-31421a122370
        jobs:
            - name: test_seed0
              pipeline: pipeline.groovy
    """)
    os.environ["LOCATION"] = "myLocation"

    proj = None
    try:
        proj = Project()
        proj.load(str(project_file.absolute()))

        assert proj.location == "myLocation"
    finally:
        del os.environ["LOCATION"]

    # ensure !ENV is needed in order to read environmental variables
    assert proj.jobs[0].scm["perforce"]["workspace"] == "depot_main_${NODE}_${JOBNAME}"
