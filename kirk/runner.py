"""
.. module:: runner
   :platform: Multiplatform
   :synopsis: Module containing source code for jenkins job executions
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import logging
import jenkins
from kirk import __version__
from kirk import KirkError
from kirk.workflow import WorkflowBuilder


class Runner:
    """
    Base class for Jenkins job runner.
    """

    def run(self, job, user=None, dev_folder="dev"):
        """
        Run a jenkins job for the given user. If ``user`` is given, the ending
        url will change according with ``dev_folder`` as following:

            * if it doesn't exist, project folder is created
            * ``dev_folder`` is merged with ``user`` in order to create
               a directory inside the project folder as following:

               ``myjenkins.com:8080/job/myproject/job/dev/job/myuser/``

        Args:
            job(:py:class:`kirk.project.JobItem`): job to run.
            user(str): user running the job.
            dev_folder(str): folder name where ``user`` jobs are stored
                (default: 'dev')

        Returns:
            str: url of the job which is building in the jenkins server.

        Raises:
            :py:class:`KirkError`: raised when some errors occur before/during job run.
        """
        raise NotImplementedError()


class JobRunner(Runner):
    """
    Jenkins job runner.
    """

    def __init__(self, credentials, owner="kirk"):
        """
        Class constructor.

        Args:
            credentials(:py:class:`Credentials`): credentials handler object.
            owner(str): owner name that handles REST API communication with
                the jenkins server.
        """
        self._logger = logging.getLogger("runner")
        self._credentials = credentials
        self._owner = owner
        self._server = None
        self._workflow = WorkflowBuilder()

    def _open_connection(self, job):
        """
        Open a connection with Jenkins server.

        Args:
            job(:py:class:`kirk.project.JobItem`): job to run.

        Returns:
            jenkins.Jenkins: Jenkins communication object.
        """
        self._logger.info("getting '%s' credentials", self._owner)
        password = self._credentials.get_password(job.server, self._owner)

        self._logger.info("connecting to '%s'", job.server)
        server = jenkins.Jenkins(job.server, self._owner, password)
        return server

    def _setup_project_folder(self, job, user=None, dev_folder="dev"):
        """
        Setup a project folder creating directories and seed job.

        Args:
            job(:py:class:`kirk.project.JobItem`): job to run.
            user(str): developer name.
            dev_folder(str): folder userd by developers.

        Returns:
            str: location of the job to run.
        """
        dev_location = job.project.location
        if user:
            dev_location = "/".join([dev_location, dev_folder, user])

        self._logger.info("setting up project folder '%s'", dev_location)

        # create the project folder
        folders = dev_location.split("/")
        base = ""

        for folder in folders:
            if base:
                base = "/".join([base, folder])
            else:
                base = folder
            if not self._server.job_exists(base):
                self._logger.info("create '%s'", base)
                self._server.create_job(base, jenkins.EMPTY_FOLDER_XML)

        return dev_location

    def _create_seed(self, location, job):
        """
        Create the job seed location.

        Args:
            location(str): job location on jenkins server.
            job(:py:class:`kirk.project.JobItem`): job to run.

        Returns:
            str: location on jenkins server.
        """
        # load the xml configuration according with scm
        seed_xml = self._workflow.build_xml(job)

        # create job seed
        seed_location = "/".join([location, job.name])

        if not self._server.job_exists(seed_location):
            self._logger.info("creating '%s'", seed_location)
            self._server.create_job(seed_location, seed_xml)
        else:
            self._logger.info("reconfigure '%s'", seed_location)
            self._server.reconfig_job(seed_location, seed_xml)

        return seed_location

    def run(self, job, user=None, dev_folder="dev"):
        if not job:
            raise ValueError("job is empty")

        if not dev_folder:
            raise ValueError("dev_folder is empty")

        url = ""

        self._server = self._open_connection(job)
        try:
            proj_folder = None

            # create project folder
            proj_folder = self._setup_project_folder(
                job,
                user=user,
                dev_folder=dev_folder)

            # create seed
            seed_location = self._create_seed(proj_folder, job)

            # run seed
            params = dict(
                KIRK_VERSION=__version__
            )
            for param in job.parameters:
                if not param.value:
                    params[param.name] = ""
                else:
                    params[param.name] = param.value

            self._server.build_job(seed_location, parameters=params)

            # get seed build url
            job_info = self._server.get_job_info(seed_location)
            url = job_info["url"] + ("%s/" % str(job_info["nextBuildNumber"]))
        except jenkins.JenkinsException as err:
            raise KirkError(err)
        finally:
            del self._server

        return url
