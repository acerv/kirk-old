"""
config module tests.
"""

import pytest
from kirk import KirkError
from kirk.config import Project


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
            - name: test_seed1
            - name: test_seed2
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
    assert len(jobs) == 3
    for i in range(0, 3):
        assert jobs[i].server == "myserver.com"
        assert jobs[i].name == "test_seed%d" % i
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
            - name: test_seed0
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
    assert jobs[0].server == "myserver2.com"
    assert jobs[0].name == "test_seed1"
    assert len(jobs[0].parameters) == 0


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
              parameters:
                - name: JK_TEST_0
                  label: Test name 0
                  default: test_something_0
                  show: false
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
    assert jobs[0].server == "myserver.com"
    assert jobs[0].name == "test_name0"
    assert len(jobs[0].parameters) == 1
    assert jobs[0].parameters[0].name == "JK_TEST_0"
    assert jobs[0].parameters[0].label == "Test name 0"
    assert jobs[0].parameters[0].default == "test_something_0"
    assert jobs[0].parameters[0].show == False
    assert jobs[0].parameters[0].value == "test_something_0"

    jobs[0].parameters[0].value = "test_something_else"
    assert jobs[0].parameters[0].value == "test_something_else"


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

    assert proj.name == "project"
    assert proj.description == "my project"
    assert proj.author == "pippo"
    assert proj.year == 3010
    assert proj.version == 1.0
    assert proj.location == "myProject"

    jobs = proj.jobs
    assert len(jobs) == 1
    assert jobs[0].server == "myserver.com"
    assert jobs[0].name == "test_name0"
    assert len(jobs[0].parameters) == 3
    for i in range(0, 3):
        assert jobs[0].parameters[i].name == "JK_TEST_%d" % i
        assert jobs[0].parameters[i].label == "Test name %d" % i
        assert jobs[0].parameters[i].default == "test_something_%d" % i
        assert jobs[0].parameters[i].show == False


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
              parameters:
                - name: JK_TEST_0
                  label: Test name 0
                  default: test_something_1
                  show: true
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
    assert jobs[0].server == "myserver.com"
    assert jobs[0].name == "test_name0"
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
    assert jobs[0].server == "myserver.com"
    assert jobs[0].name == "test_name0"
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
            - name: test_name1
              depends:
                - test_name0
            - name: test_name2
              depends:
                - test_name0
                - test_name1
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
    assert len(jobs) == 3
    assert jobs[0].server == "myserver.com"
    assert jobs[0].name == "test_name0"
    assert jobs[1].server == "myserver.com"
    assert jobs[1].name == "test_name1"
    assert jobs[1].dependences == ["test_name0"]
    assert jobs[2].server == "myserver.com"
    assert jobs[2].name == "test_name2"
    assert jobs[2].dependences == ["test_name0", "test_name1"]
