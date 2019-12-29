"""
.. module:: checker
   :platform: Multiplatform
   :synopsis: testing module for jenkins server
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import os
import time
import xml.dom.minidom
import yaml
import jenkins
from kirk import KirkError


class Tester:
    """
    Base class for a Jenkins server tester.
    """

    def test_connection(self):
        """
        Test if Jenkins server accepts a connection.
        """
        raise NotImplementedError()

    def test_plugins(self):
        """
        Test if Jenkins server has the minimum plugins requirements.
        """
        raise NotImplementedError()

    def test_job_create(self):
        """
        Test if Jenkins server accepts job creation.
        """
        raise NotImplementedError()

    def test_job_config(self):
        """
        Test if Jenkins server accepts job configuration.
        """
        raise NotImplementedError()

    def test_job_info(self):
        """
        Test if Jenkins server accepts fetching job information.
        """
        raise NotImplementedError()

    def test_job_build(self):
        """
        Test if Jenkins server accepts job build.
        """
        raise NotImplementedError()

    def test_job_delete(self):
        """
        Test if Jenkins server accepts job delete.
        """
        raise NotImplementedError()


class JenkinsTester:
    """
    Implementation of a Jenkins tester.
    """

    TEST_JOB = "__kirk_delete_me"

    def __init__(self, url, username, password):
        """
        :param url: jenkins server url
        :type url: str
        :param username: jenkins user
        :type username: str
        :param password: jenkins user password
        :type password: str
        """
        self._url = url
        self._username = username
        self._password = password
        self._server = jenkins.Jenkins(
            self._url,
            self._username,
            self._password)
        self._config = None

        currdir = os.path.abspath(os.path.dirname(__file__))
        config_path = os.path.join(currdir, "files", "defaults.yml")

        with open(config_path) as config_data:
            self._config = yaml.safe_load(config_data)

    def _prettify_xml(self, xml_str):
        """
        Prettify a xml string.

        Args:
            xml_str(str): A xml string to prettify.

        Returns:
            str: prettified xml_str.
        """
        dom = xml.dom.minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml()

        # remove the double newline which is terrible in toprettyxml
        pretty_xml = os.linesep.join(
            [s for s in pretty_xml.splitlines() if s.strip()])
        return pretty_xml

    def test_connection(self):
        username = None
        try:
            username = self._server.get_whoami()['fullName']
        except jenkins.JenkinsException as err:
            raise KirkError(err)

        if username != self._username:
            raise KirkError(
                "read username '%s' != '%s'" %
                (username, self._username))

    def test_plugins(self):
        def_plugins = self._config['kirk']['jenkins']['plugins']

        plugins_info = None
        try:
            plugins_info = self._server.get_plugins_info()
        except jenkins.JenkinsException as err:
            raise KirkError(err)

        plugins_names = [item['shortName'] for item in plugins_info]

        for plugin in def_plugins:
            plugin_name = plugin['name']
            plugin_opt = plugin['optional']
            plugin_found = plugin_name in plugins_names

            if not plugin_found and not plugin_opt:
                raise KirkError("'%s' plugin is required" % plugin_name)

    def test_job_create(self):
        xml_str = """<?xml version='1.1' encoding='UTF-8'?>
            <flow-definition plugin="workflow-job">
                <description>Testing job for kirk-check command</description>
                <keepDependencies>false</keepDependencies>
                <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
                    <script></script>
                    <sandbox>true</sandbox>
                </definition>
                <triggers/>
                <disabled>false</disabled>
            </flow-definition>
        """
        xml_str = self._prettify_xml(xml_str)
        try:
            self._server.create_job(self.TEST_JOB, xml_str)
        except jenkins.JenkinsException as err:
            raise KirkError(err)

    def test_job_config(self):
        xml_str = """<?xml version='1.1' encoding='UTF-8'?>
            <flow-definition plugin="workflow-job">
                <description>Testing job for kirk-check command</description>
                <keepDependencies>false</keepDependencies>
                <properties>
                    <hudson.model.ParametersDefinitionProperty>
                        <parameterDefinitions>
                            <hudson.model.StringParameterDefinition>
                                <name>NAME</name>
                                <description>Name of the guy to greet</description>
                                <defaultValue>gigi</defaultValue>
                                <trim>false</trim>
                            </hudson.model.StringParameterDefinition>
                        </parameterDefinitions>
                    </hudson.model.ParametersDefinitionProperty>
                </properties>
                <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
                    <script></script>
                    <sandbox>true</sandbox>
                </definition>
                <triggers/>
                <disabled>false</disabled>
            </flow-definition>
        """
        xml_str = self._prettify_xml(xml_str)
        try:
            self._server.reconfig_job(self.TEST_JOB, xml_str)
        except jenkins.JenkinsException as err:
            raise KirkError(err)

    def test_job_info(self):
        try:
            self._server.get_job_info(self.TEST_JOB)
        except jenkins.JenkinsException as err:
            raise KirkError(err)

    def test_job_build(self):
        try:
            self._server.build_job(
                self.TEST_JOB,
                parameters=dict(NAME="pluto"))

            while True:
                job_info = self._server.get_job_info(self.TEST_JOB)
                last_build = job_info['lastCompletedBuild']
                if last_build and 'number' in last_build:
                    break
                time.sleep(0.1)
        except jenkins.JenkinsException as err:
            raise KirkError(err)

    def test_job_delete(self):
        try:
            self._server.delete_job(self.TEST_JOB)
        except jenkins.JenkinsException as err:
            raise KirkError(err)
