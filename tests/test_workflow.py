"""
workflow module tests.
"""
from kirk.project import Project
from kirk.workflow import GitSCMFlow
import xml.etree.ElementTree as ET


def test_gitflow(tmp_path):
    """
    Test GitSCMFlow implementation
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

    builder = GitSCMFlow()
    xml = builder.build_xml(proj.jobs[0])

    tree = ET.fromstring(xml)
    assert tree is not None
