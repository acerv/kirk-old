"""
workflow module tests.
"""
import xml.etree.ElementTree as ET
import kirk.workflow
from kirk.project import Project


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
                    credential: fbf1e43a-3442-455e-9c7f-31421a122370
        jobs:
            - name: test_seed1
              pipeline: pipeline.groovy
    """)
    proj = Project()
    proj.load(str(project_file.absolute()))

    xml_str = kirk.workflow.build_xml(proj.jobs[0], change_id="my_branch")

    tree = ET.fromstring(xml_str)
    tags = dict()
    for item in tree.iter():
        tags[item.tag] = item.text

    assert tree is not None
    assert "url" in tags and tags['url'] == "myurl.com/repo.git"
    assert "credentialsId" in tags and tags['credentialsId'] == "fbf1e43a-3442-455e-9c7f-31421a122370"
    assert "name" in tags and tags['name'] == "my_branch"
    assert "scriptPath" in tags and tags['scriptPath'] == "pipeline.groovy"


def test_p4flow(tmp_path):
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
                perforce:
                    stream: //depot/main
                    workspace: depot_main_workspace
                    credential: fbf1e43a-3442-455e-9c7f-31421a122370
        jobs:
            - name: test_seed1
              pipeline: pipeline.groovy
    """)
    proj = Project()
    proj.load(str(project_file.absolute()))

    xml_str = kirk.workflow.build_xml(proj.jobs[0], change_id="654321")

    tree = ET.fromstring(xml_str)
    tags = dict()
    for item in tree.iter():
        tags[item.tag] = item.text

    assert tree is not None
    assert "streamName" in tags and tags['streamName'] == "//depot/main"
    assert "name" in tags and tags['name'] == "depot_main_workspace"
    assert "credential" in tags and tags['credential'] == "fbf1e43a-3442-455e-9c7f-31421a122370"
    assert "scriptPath" in tags and tags['scriptPath'] == "pipeline.groovy"
    assert "shelf" in tags and tags['shelf'] == "654321"


def test_scriptflow(tmp_path):
    """
    Test ScriptFlow implementation
    """
    script_file = tmp_path / "script.groovy"
    script_file.write_text("""
    node
    {
        println "hello world"
    }
    """)
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
                    script: %s
                    sandbox: false
        jobs:
            - name: test_seed1
    """ % script_file.absolute())
    proj = Project()
    proj.load(str(project_file.absolute()))

    xml_str = kirk.workflow.build_xml(proj.jobs[0])

    tree = ET.fromstring(xml_str)
    tags = dict()
    for item in tree.iter():
        tags[item.tag] = item.text

    assert tree is not None
    assert "script" in tags and tags['script'] == """
    node
    {
        println "hello world"
    }
    """
    assert "sandbox" in tags and tags['sandbox'] == "false"
