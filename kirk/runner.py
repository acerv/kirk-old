"""
.. module:: runner
   :platform: Multiplatform
   :synopsis: Module containing source code for jenkins job executions
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import logging
import jenkins
import kirk.workflow
from kirk import __version__


class Runner:
    """
    base class for Jenkins job runner.
    """

    def run(self, job, user=None, dev_folder="dev"):
        """
        Run a jenkins job for the given user.
        :param job: job to run
        :type job: JobItem
        :param user: user name running the job. This parameter is used to
            create the jenkins job. For example, if user="myuser", the ending
            job will be stored inside the following folder:

                myjenkins.com:8080/job/myproject/job/dev/job/myuser/job/myjob/

            If no user has provided, job will be created and run inside the
            main project folder. For example:

                myjenkins.com:8080/job/myproject/job/myjob/

        :param dev_folder: folder where user jobs are stored (default: 'dev')
        :type dev_folder: str
        :return: url as string where job has been created
        """
        raise NotImplementedError()


class JobRunner(Runner):
    """
    Jenkins job runner.
    """

    def __init__(self, credentials, owner="kirk"):
        """
        :param credentials: credentials handler object
        :type credentials: Credentials
        :param projects: list of the projects to load
        :type projects: list(Project)
        :param owner: owner username to create jobs in the jenkins server
        :type owner: str
        """
        self._logger = logging.getLogger("runner")
        self._credentials = credentials
        self._owner = owner
        self._server = None

    def _open_connection(self, job):
        """
        Open a connection with Jenkins server.
        """
        self._logger.info("getting '%s' credentials", self._owner)
        password = self._credentials.get_password(job.server, self._owner)

        self._logger.info("connecting to '%s'", job.server)
        server = jenkins.Jenkins(job.server, self._owner, password)
        return server

    def _setup_project_folder(self, job, user=None, dev_folder="dev"):
        """
        Setup a project folder creating directories and seed job.
        Return the project location.
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
        """
        # load the xml configuration according with scm
        seed_xml = kirk.workflow.build_xml(job)

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
            raise ValueError("job is None")

        if not dev_folder:
            raise ValueError("dev_folder is empty")

        self._server = self._open_connection(job)
        try:
            proj_folder = None

            # create project folder
            proj_folder = self._setup_project_folder(job, user)

            # create seed
            seed_location = self._create_seed(proj_folder, job)

            # run seed
            params = dict(
                KIRK_VERSION=__version__
            )
            for param in job.parameters:
                params[param.name] = param.value

            self._server.build_job(seed_location, parameters=params)
        finally:
            del self._server

        url = job.server + "/" + seed_location
        return url
