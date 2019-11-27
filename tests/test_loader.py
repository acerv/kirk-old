"""
loader module tests.
"""

import pytest
import kirk.loader
from kirk import KirkError


def test_load_conflicts(tmp_path):
    """
    Test Runner::load method when there are two or more projects
    with the same name.
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
              parameters:
                - name: JK_HELLO_MSG
                  default: Hello from Kirk 0
                  label: Hello message
                  show: false
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
              parameters:
                - name: JK_HELLO_MSG
                  default: Hello from Kirk 1
                  label: Hello message
                  show: false
    """)
    with pytest.raises(KirkError):
        kirk.loader.load(str(tmp_path))
