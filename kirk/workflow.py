"""
.. module:: workflow
   :platform: Multiplatform
   :synopsis: xml workflow jobs generator
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import re
from datetime import date
from kirk import KirkError


class XmlBuilder:
    """
    A generic builder translating parts of a JenkinsJob object into
    XML source code.
    """

    def __init__(self):
        self._re_pattern = re.compile(r'(?P<variable>KIRK_\w+)')

    def _create_param_xml(self, name, label, value):
        """
        create the xml for a job single parameter
        """
        xml = """
            <hudson.model.StringParameterDefinition>
            <name>%s</name>
            <description>%s</description>
            <defaultValue>%s</defaultValue>
            <trim>false</trim>
            </hudson.model.StringParameterDefinition>
        """ % (name, label, value)
        return xml

    def _create_params_xml(self, job):
        """
        create the xml for job parameters
        """
        xml_params = list()
        xml_params.append("<hudson.model.ParametersDefinitionProperty>")
        xml_params.append("<parameterDefinitions>\n")

        # always add kirk version to parametrize tests
        xml = self._create_param_xml(
            'KIRK_VERSION',
            'Kirk version',
            '0.0')
        xml_params.append(xml)

        if job.parameters:
            for param in job.parameters:
                xml = self._create_param_xml(
                    param.name,
                    param.label,
                    param.value)
                xml_params.append(xml)

        xml_params.append("</parameterDefinitions>")
        xml_params.append("</hudson.model.ParametersDefinitionProperty>")

        return '\n'.join(xml_params)

    def _replace_xml_params(self, xml, params):
        """
        Search inside XML the given parameters and replace them.
        """
        seed_xml = re.sub(
            self._re_pattern,
            lambda m: params[m.group('variable')],
            xml)

        return seed_xml

    def build_xml(self, job):
        """
        Generate xml code according with a Jenkins job definition.
        :param job: jenkins job configuration object
        :type job: JenkinsJob
        :return: xml code as str
        """
        raise NotImplementedError()


class GitSCMFlow(XmlBuilder):
    """
    GIT SCM flow xml generator. It generates something like:
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
        <lightweight>true</lightweight>
    </definition>
    <triggers/>
    <disabled>false</disabled>
</flow-definition>
    """

    def build_xml(self, job):
        if not job.scm:
            return None

        if 'git' not in job.scm:
            return None

        params = dict()
        params["KIRK_DESCRIPTION"] = "Created by kirk in date %s" % date.today()
        params["KIRK_SCRIPT_PATH"] = job.pipeline
        params["KIRK_GIT_CREDENTIAL"] = job.scm["git"].get("credential", "")
        params["KIRK_GIT_URL"] = job.scm["git"]["url"]
        params["KIRK_GIT_CHECKOUT"] = job.scm["git"]["checkout"]
        params['KIRK_PARAMETERS'] = self._create_params_xml(job)

        seed_xml = self._replace_xml_params(self.SEED_XML, params)
        return seed_xml


class PerforceSCMFlow(XmlBuilder):
    """
    Perforce SCM flow xml generator.
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
        <shelf>KIRK_P4_CL</shelf>
        <ignoreEmpty>false</ignoreEmpty>
        <resolve>none</resolve>
        <tidy>false</tidy>
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
            <pin></pin>
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

    def build_xml(self, job):
        if not job.scm:
            return None

        if 'perforce' not in job.scm:
            return None

        params = dict()
        params["KIRK_DESCRIPTION"] = "Created by kirk in date %s" % date.today()
        params["KIRK_SCRIPT_PATH"] = job.pipeline
        params["KIRK_P4_CREDENTIAL"] = job.scm["perforce"]["credential"]
        params["KIRK_P4_CL"] = str(job.scm["perforce"]["changelist"])
        params["KIRK_P4_WORKSPACE"] = job.scm["perforce"]["workspace"]
        params["KIRK_P4_STREAM"] = job.scm["perforce"]["stream"]
        params['KIRK_PARAMETERS'] = self._create_params_xml(job)

        seed_xml = self._replace_xml_params(self.SEED_XML, params)
        return seed_xml


class SandboxScriptFlow(XmlBuilder):
    """
    Scripted flow xml generator.
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
        <script>KIRK_SCRIPT_PATH</script>
        <sandbox>true</sandbox>
    </definition>
    <triggers/>
    <disabled>false</disabled>
</flow-definition>
    """

    def build_xml(self, job):
        if job.scm:
            return None

        params = dict()
        params["KIRK_DESCRIPTION"] = "Created by kirk in date %s" % date.today()
        params["KIRK_SCRIPT_PATH"] = job.pipeline
        params['KIRK_PARAMETERS'] = self._create_params_xml(job)

        seed_xml = self._replace_xml_params(self.SEED_XML, params)
        return seed_xml


# builders used by build_xml method
BUILDERS = [
    GitSCMFlow(),
    PerforceSCMFlow(),
    SandboxScriptFlow()
]


def build_xml(job):
    """
    Generate the xml code of a workflow with a Jenkins job definition.
    :param job: jenkins job configuration object
    :type job: JenkinsJob
    :return: xml code as str
    """
    xml = None
    for builder in BUILDERS:
        xml = builder.build_xml(job)
        if xml:
            break

    if not xml:
        raise KirkError("Unsupported SCM configuration:\n" % str(job.scm))

    return xml
