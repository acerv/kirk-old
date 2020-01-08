"""
.. module:: workflow
   :platform: Multiplatform
   :synopsis: xml workflow jobs generator
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import os
import re
import xml.dom.minidom
from datetime import date
from kirk import KirkError


class XmlBuilder:
    """
    A generic builder class a :py:class:`kirk.project.JobItem` object into
    a XML string.
    """

    def __init__(self):
        self._re_pattern = re.compile(r'(?P<variable>KIRK_\w+)')

    @staticmethod
    def _create_param_xml(name, label, value):
        """
        create the xml for a job single parameter
        """
        xml_str = """
            <hudson.model.StringParameterDefinition>
            <name>%s</name>
            <description>%s</description>
            <defaultValue>%s</defaultValue>
            <trim>false</trim>
            </hudson.model.StringParameterDefinition>
        """ % (name, label, value)
        return xml_str

    def _create_params_xml(self, job):
        """
        create the xml for job parameters
        """
        xml_params = list()
        xml_params.append("<hudson.model.ParametersDefinitionProperty>")
        xml_params.append("<parameterDefinitions>\n")

        # always add kirk version to parametrize tests
        xml_str = self._create_param_xml(
            'KIRK_VERSION',
            'Kirk version',
            '0.0')
        xml_params.append(xml_str)

        if job.parameters:
            for param in job.parameters:
                xml_str = self._create_param_xml(
                    param.name,
                    param.label,
                    param.value)
                xml_params.append(xml_str)

        xml_params.append("</parameterDefinitions>")
        xml_params.append("</hudson.model.ParametersDefinitionProperty>")

        return '\n'.join(xml_params)

    def _replace_xml_params(self, xml_str, params):
        """
        Search inside XML the given parameters and replace them.
        """
        seed_xml = re.sub(
            self._re_pattern,
            lambda m: params[m.group('variable')],
            xml_str)

        return seed_xml

    def build_xml(self, job, change_id=""):
        """
        Converts the ``job`` item into a Jenkins job XML configuration.

        Args:
            job(:py:class:`kirk.project.JobItem`): job item to convert.
            change_id(str): change identifier storing source code modifications.
                For example, in Git, ``change_id`` might be the commit hash
                string. In Perforce it will be the changelist number.

        Returns:
            str: Jenkins job XML configuration.
        """
        raise NotImplementedError()


class _GitSCMFlow(XmlBuilder):
    """
    GIT SCM flow XML generator.
    """

    SEED_XML = """<?xml version='1.1' encoding='UTF-8'?>
        <flow-definition plugin="workflow-job">
            <!-- Generics -->
            <description>KIRK_DESCRIPTION</description>
            <keepDependencies>false</keepDependencies>
            <properties>
            KIRK_PARAMETERS
            </properties>
            <!-- SCM pipeline setup -->
            <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps">
                <scm class="hudson.plugins.git.GitSCM" plugin="git">
                <configVersion>2</configVersion>
                <userRemoteConfigs>
                    <hudson.plugins.git.UserRemoteConfig>
                    <url>KIRK_GIT_URL</url>
                    <credentialsId>KIRK_GIT_CREDENTIAL</credentialsId>
                    </hudson.plugins.git.UserRemoteConfig>
                </userRemoteConfigs>
                <branches>
                    <hudson.plugins.git.BranchSpec>
                    <name>KIRK_GIT_CHECKOUT</name>
                    </hudson.plugins.git.BranchSpec>
                </branches>
                <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
                <submoduleCfg class="list"/>
                <extensions/>
                </scm>
                <scriptPath>KIRK_SCRIPT_PATH</scriptPath>
                <lightweight>false</lightweight>
            </definition>
            <triggers/>
            <disabled>false</disabled>
        </flow-definition>
    """

    def build_xml(self, job, change_id=""):
        if not job.scm:
            return None

        if 'git' not in job.scm:
            return None

        checkout = "master"
        if change_id:
            checkout = change_id

        params = dict()
        params["KIRK_DESCRIPTION"] = "Created by kirk in date %s" % date.today()
        params["KIRK_SCRIPT_PATH"] = job.pipeline
        params["KIRK_GIT_CREDENTIAL"] = job.scm["git"].get("credential", "")
        params["KIRK_GIT_URL"] = job.scm["git"]["url"]
        params["KIRK_GIT_CHECKOUT"] = checkout
        params['KIRK_PARAMETERS'] = self._create_params_xml(job)

        seed_xml = self._replace_xml_params(self.SEED_XML, params)
        return seed_xml


class _PerforceSCMFlow(XmlBuilder):
    """
    Perforce SCM flow XML generator.
    """

    SEED_XML = """<?xml version='1.1' encoding='UTF-8'?>
        <flow-definition plugin="workflow-job">
            <!-- Generics -->
            <description>KIRK_DESCRIPTION</description>
            <keepDependencies>false</keepDependencies>
            <properties>
            KIRK_PARAMETERS
            </properties>
            <!-- SCM pipeline setup -->
            <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps">
                <scm class="org.jenkinsci.plugins.p4.PerforceScm" plugin="p4">
                <credential>KIRK_P4_CREDENTIAL</credential>
                <workspace class="org.jenkinsci.plugins.p4.workspace.ManualWorkspaceImpl">
                    <charset>none</charset>
                    <pinHost>false</pinHost>
                    <name>KIRK_P4_WORKSPACE</name>
                    <spec>
                    <allwrite>false</allwrite>
                    <clobber>true</clobber>
                    <compress>false</compress>
                    <locked>false</locked>
                    <modtime>false</modtime>
                    <rmdir>false</rmdir>
                    <streamName>KIRK_P4_STREAM</streamName>
                    <line>LOCAL</line>
                    <view></view>
                    <type>WRITABLE</type>
                    <serverID></serverID>
                    <backup>false</backup>
                    </spec>
                </workspace>
                <populate class="org.jenkinsci.plugins.p4.populate.AutoCleanImpl">
                    <have>true</have>
                    <force>false</force>
                    <modtime>false</modtime>
                    <quiet>true</quiet>
                    <pin>KIRK_P4_CL</pin>
                    <parallel>
                    <enable>false</enable>
                    <threads>4</threads>
                    <minfiles>1</minfiles>
                    <minbytes>1024</minbytes>
                    </parallel>
                    <replace>true</replace>
                    <delete>true</delete>
                    <tidy>false</tidy>
                </populate>
                </scm>
                <scriptPath>KIRK_SCRIPT_PATH</scriptPath>
                <lightweight>true</lightweight>
            </definition>
            <triggers/>
            <disabled>false</disabled>
        </flow-definition>
    """

    def build_xml(self, job, change_id=""):
        if not job.scm:
            return None

        if 'perforce' not in job.scm:
            return None

        changelist = "latest"
        if change_id:
            # it will raise a ValueError exception is it's not an int
            int(change_id)
            changelist = change_id

        params = dict()
        params["KIRK_DESCRIPTION"] = "Created by kirk in date %s" % date.today()
        params["KIRK_SCRIPT_PATH"] = job.pipeline
        params["KIRK_P4_CREDENTIAL"] = job.scm["perforce"]["credential"]
        params["KIRK_P4_CL"] = changelist
        params["KIRK_P4_WORKSPACE"] = job.scm["perforce"]["workspace"]
        params["KIRK_P4_STREAM"] = job.scm["perforce"]["stream"]
        params['KIRK_PARAMETERS'] = self._create_params_xml(job)

        seed_xml = self._replace_xml_params(self.SEED_XML, params)
        return seed_xml


class _ScriptFlow(XmlBuilder):
    """
    Scripted flow XML generator.
    """

    SEED_XML = """<?xml version='1.1' encoding='UTF-8'?>
        <flow-definition plugin="workflow-job">
            <!-- Generics -->
            <description>KIRK_DESCRIPTION</description>
            <keepDependencies>false</keepDependencies>
            <properties>
            KIRK_PARAMETERS
            </properties>
            <!-- SCM pipeline setup -->
            <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
                <script>KIRK_SCRIPT_CODE</script>
                <sandbox>KIRK_SCRIPT_SANDBOX</sandbox>
            </definition>
            <triggers/>
            <disabled>false</disabled>
        </flow-definition>
    """

    def build_xml(self, job, change_id=""):
        if job.scm is None or 'none' not in job.scm:
            return None

        del change_id

        params = dict()
        params["KIRK_DESCRIPTION"] = "Created by kirk in date %s" % date.today()
        params['KIRK_PARAMETERS'] = self._create_params_xml(job)
        params["KIRK_SCRIPT_CODE"] = ""

        # read script data
        script = ""
        with open(job.scm['none']['script'], 'r') as script_txr:
            script = script_txr.read()

        if 'none' in job.scm:
            params["KIRK_SCRIPT_CODE"] = script
            sandbox = job.scm['none'].get('sandbox', '')
            if sandbox:
                params["KIRK_SCRIPT_SANDBOX"] = 'true'
            else:
                params["KIRK_SCRIPT_SANDBOX"] = 'false'

        seed_xml = self._replace_xml_params(self.SEED_XML, params)
        return seed_xml


class WorkflowBuilder(XmlBuilder):
    """
    The main workflow XML builder.
    """

    _BUILDERS = [
        _GitSCMFlow(),
        _PerforceSCMFlow(),
        _ScriptFlow()
    ]

    def build_xml(self, job, change_id=""):
        xml_str = None
        for builder in self._BUILDERS:
            xml_str = builder.build_xml(job, change_id)
            if xml_str:
                break

        if not xml_str:
            raise KirkError(
                "Unsupported SCM configuration:\n%s" % str(job.scm))

        dom = xml.dom.minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml()

        # remove the double newline which is terrible in toprettyxml
        pretty_xml = os.linesep.join(
            [s for s in pretty_xml.splitlines() if s.strip()])

        return pretty_xml
