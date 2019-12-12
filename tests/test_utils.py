"""
loader module tests.
"""

import pytest
import kirk.utils
from kirk import KirkError


def test_get_projects_from_folder(tmp_path):
    """
    Test get_projects_from_folder method
    """
    project_file0 = tmp_path / "project0.yml"
    project_file0.write_text("""
        name: project1
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject1
        defaults:
            server: http://localhost:8080
        jobs:
            - name: test_name0
              pipeline: pipeline.groovy
    """)
    project_file1 = tmp_path / "project1.yml"
    project_file1.write_text("""
        name: project2
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject2
        defaults:
            server: http://localhost:8080
        jobs:
            - name: test_name0
              pipeline: pipeline.groovy
    """)
    projects = kirk.utils.get_projects_from_folder(str(tmp_path))
    assert len(projects) == 2
    assert projects[0].name == "project1"
    assert projects[1].name == "project2"


def test_get_projects_from_folder_error(tmp_path):
    """
    Test get_projects_from_folder method when raises exceptions
    """
    project_file0 = tmp_path / "project0.yml"
    project_file0.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: http://localhost:8080
        jobs:
            - name: test_name0
              pipeline: pipeline.groovy
    """)
    project_file1 = tmp_path / "project1.yml"
    project_file1.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: http://localhost:8080
        jobs:
            - name: test_name0
              pipeline: pipeline.groovy
    """)
    with pytest.raises(ValueError, match="folder is empty"):
        kirk.utils.get_projects_from_folder(None)

    with pytest.raises(ValueError, match="folder is empty"):
        kirk.utils.get_projects_from_folder("")

    with pytest.raises(ValueError, match="folder is not a directory"):
        kirk.utils.get_projects_from_folder("asda3fasds")

    with pytest.raises(KirkError, match="Two projects with the same name"):
        kirk.utils.get_projects_from_folder(str(tmp_path))


def test_get_jobs_from_folder(tmp_path):
    """
    Test get_projects_from_folder method
    """
    project_file0 = tmp_path / "project0.yml"
    project_file0.write_text("""
        name: project1
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject1
        defaults:
            server: http://localhost:8080
        jobs:
            - name: test_name0
              pipeline: pipeline.groovy
    """)
    project_file1 = tmp_path / "project1.yml"
    project_file1.write_text("""
        name: project2
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject2
        defaults:
            server: http://localhost:8080
        jobs:
            - name: test_name0
              pipeline: pipeline.groovy
            - name: test_name1
              pipeline: pipeline.groovy
    """)
    jobs = kirk.utils.get_jobs_from_folder(str(tmp_path))
    assert len(jobs) == 3
    assert str(jobs[0]) == "project1::test_name0"
    assert str(jobs[1]) == "project2::test_name0"
    assert str(jobs[2]) == "project2::test_name1"


def test_get_jobs_from_folder_error(tmp_path):
    """
    Test get_jobs_from_folder method when raises exceptions
    """
    project_file0 = tmp_path / "project0.yml"
    project_file0.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: http://localhost:8080
        jobs:
            - name: test_name0
              pipeline: pipeline.groovy
    """)
    project_file1 = tmp_path / "project1.yml"
    project_file1.write_text("""
        name: project
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject
        defaults:
            server: http://localhost:8080
        jobs:
            - name: test_name0
              pipeline: pipeline.groovy
    """)
    with pytest.raises(ValueError, match="folder is empty"):
        kirk.utils.get_jobs_from_folder(None)

    with pytest.raises(ValueError, match="folder is empty"):
        kirk.utils.get_jobs_from_folder("")

    with pytest.raises(ValueError, match="folder is not a directory"):
        kirk.utils.get_jobs_from_folder("asda3fasds")

    with pytest.raises(KirkError, match="Two projects with the same name"):
        kirk.utils.get_jobs_from_folder(str(tmp_path))


def test_get_project_regexp(tmp_path):
    """
    Test get_project_regexp.
    """
    project_file0 = tmp_path / "project0.yml"
    project_file0.write_text("""
        name: project1
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject1
        defaults:
            server: http://localhost:8080
        jobs:
            - name: test_name0
              pipeline: pipeline.groovy
            - name: test_name1
              pipeline: pipeline.groovy
    """)
    project_file1 = tmp_path / "project1.yml"
    project_file1.write_text("""
        name: project2
        description: my project
        author: pippo
        year: 3010
        version: 1.0
        location: myProject2
        defaults:
            server: http://localhost:8080
        jobs:
            - name: test_name2
              pipeline: pipeline.groovy
            - name: test_name3
              pipeline: pipeline.groovy
    """)
    projects = kirk.utils.get_projects_from_folder(str(tmp_path))
    filtered = kirk.utils.get_project_regexp(".*test.*", projects)

    assert len(filtered) == 4
    for i in range(0, 4):
        assert filtered[i].name == "test_name%d" % i

    filtered = kirk.utils.get_project_regexp(".*0.*", projects)
    assert len(filtered) == 1
    assert filtered[0].name == "test_name0"

    filtered = kirk.utils.get_project_regexp("project1::test_name0", projects)
    assert len(filtered) == 1
    assert filtered[0].name == "test_name0"


def test_get_project_regexp_errors(tmp_path):
    """
    Test get_project_regexp when errors are thrown
    """
    with pytest.raises(ValueError, match="regexp is not defined"):
        kirk.utils.get_project_regexp("", None)

    with pytest.raises(ValueError, match="projects are empty"):
        kirk.utils.get_project_regexp(".*name.*", None)
