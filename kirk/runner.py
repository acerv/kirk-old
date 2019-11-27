"""
.. module:: runner
   :platform: Multiplatform
   :synopsis: Module containing source code for jenkins job executions
   :license: GPLv2
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import logging
import jenkins
from kirk import KirkError


class Runner:
    """
    Runner class for projects files.
    """

    def __init__(self, user, token, projects):
        """
        :param user: username to login in jenkins
        :type user: str
        :param token: token of the username in jenkins
        :type token: str
        :param projects: list of the projects to load
        :type projects: list(Project)
        """
        if not user:
            raise ValueError('user')

        if not token:
            raise ValueError('token')

        self._logger = logging.getLogger("runner")
        self._projects = projects
        self._user = user
        self._token = token
        self._server = None

    def _open_connection(self, job):
        """
        Open a connection with Jenkins server.
        """
        self._logger.info("connecting to '%s'", job.server)
        server = jenkins.Jenkins(job.server, self._user, self._token)
        return server

    def _setup_project_folder(self, location):
        """
        Setup a project folder creating directories and seed job.
        Return the seed location.
        """
        self._logger.info("setting up project folder '%s'", location)

        # create the project folder
        folders = location.split("/")
        base = ""

        for folder in folders:
            if base:
                base = "/".join([base, folder])
            else:
                base = folder
            if not self._server.job_exists(base):
                self._logger.info("create '%s'", base)
                self._server.create_job(base, jenkins.EMPTY_FOLDER_XML)

    def _create_seed(self, location, job):
        """
        Create the job seed location.
        """
        # create the seed
        seed_xml = '''<?xml version='1.0' encoding='UTF-8'?>
        <project>
            <actions/>
            <description>Created by kirk</description>
            <scm class="hudson.scm.NullSCM"/>
        </project>'''
        seed_location = "/".join([location, job.name])

        if not self._server.job_exists(seed_location):
            self._logger.info("creating '%s'", seed_location)
            self._server.create_job(seed_location, seed_xml)
        else:
            self._logger.info("reconfigure '%s'", seed_location)
            self._server.reconfig_job(seed_location, seed_xml)

        return seed_location

    def _setup_developer_folder(self, location):
        """
        Setup the developer folders inside given location.
        """
        dev_location = "/".join([location, "dev", self._user])
        self._setup_project_folder(dev_location)
        return dev_location

    def _run(self, proj_name, job_name, mode="developer"):
        """
        Run a job for the given project.
        """
        if not proj_name:
            raise ValueError("proj_name")

        if not job_name:
            raise ValueError("job_name")

        if not self._projects:
            raise KirkError("No projects loaded")

        # find the project
        project = None
        for proj in self._projects:
            if proj.name == proj_name:
                project = proj
                break

        if not project:
            raise KirkError("No project with name '%s'" % proj_name)

        if not project.jobs:
            raise KirkError("No jobs found for project '%s'" % proj_name)

        # find the job
        job_to_run = None
        for job in project.jobs:
            if job.name == job_name:
                job_to_run = job
                break

        self._server = self._open_connection(job_to_run)
        try:
            proj_folder = None

            # create folders as developer if needed
            if mode == "developer":
                proj_folder = self._setup_developer_folder(proj.location)
            else:
                self._setup_project_folder(proj.location)
                proj_folder = proj.location

            # create seed
            seed_location = self._create_seed(proj_folder, job_to_run)

            # run seed
            params = dict()
            for param in job.parameters:
                params[param.name] = param.value

            self._server.build_job(seed_location, parameters=params)
        finally:
            del self._server

    def run_as_developer(self, proj_name, job_name):
        """
        Run a job as developer of the project.
        :param proj_name: project name
        :type proj_name: str
        :param job_name: job name
        :type job_name: str
        """
        self._run(proj_name, job_name, mode="developer")

    def run_as_owner(self, proj_name, job_name):
        """
        Run a job as the owner of the project.
        :param proj_name: project name
        :type proj_name: str
        :param job_name: job name
        :type job_name: str
        """
        self._run(proj_name, job_name, mode="owner")
