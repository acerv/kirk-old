"""
.. module:: project
   :platform: Multiplatform
   :synopsis: project handling module
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import os
import logging
from pykwalify.core import Core
from pykwalify.errors import PyKwalifyException
import kirk.yaml_env as yaml_env
from kirk import KirkError
from kirk.tokenizer import JobTokenizer


class JobParameter:
    """
    Jenkins job parameter.
    """

    def __init__(self, params_cfg):
        self._name = params_cfg['name']
        self._label = params_cfg['label']
        self._default = params_cfg.get('default', '')
        self._value = params_cfg.get('default', '')
        self._show = params_cfg.get('show', True)

    def __str__(self):
        param = "%s=%s" % (self._name, self._value)
        return param

    @property
    def name(self):
        """
        str: Name of the job parameter.
        """
        return self._name

    @property
    def label(self):
        """
        str: A label for the job parameter.
        """
        return self._label

    @property
    def default(self):
        """
        str: Default value of the job parameter.
        """
        return self._default

    @property
    def show(self):
        """
        bool: If true, the parameter has to be shown.
        """
        return self._show

    @property
    def value(self):
        """
        str: Parameter value.
        """
        return self._value

    @value.setter
    def value(self, value):
        self._value = str(value)


class JobItem:
    """
    A generic job loaded from a project.
    """

    def __init__(self, defaults_cfg, job_cfg, project):
        self._tokenizer = JobTokenizer()

        # read server url
        # TODO: validate url syntax
        self._server = defaults_cfg['server']
        if 'server' in job_cfg:
            self._server = job_cfg['server']

        # name of the job
        self._name = job_cfg['name']

        # pipeline of the job
        self._pipeline = job_cfg.get('pipeline', '')

        # scm of the job
        self._scm = defaults_cfg.get('scm', None)

        # read dependences
        self._dependences = list()
        if 'depends' in job_cfg:
            self._dependences.extend(job_cfg['depends'])

        # read default parameters
        def_params = None
        if 'parameters' in defaults_cfg:
            def_params = defaults_cfg['parameters']

        # read job parameters
        job_params = None
        if 'parameters' in job_cfg:
            job_params = job_cfg['parameters']

        # project location in the jenkins server
        self._project = project

        # merge parameters
        parameters = list()

        if job_params:
            # priority to job parameters..
            for job_param in job_params:
                parameters.append(job_param)

        if def_params:
            # ..then to default parameters
            for def_param in def_params:
                conflict = False

                for param in parameters:
                    if param['name'] == def_param['name']:
                        conflict = True
                        break

                if not conflict:
                    parameters.append(def_param)

        # create parameters list
        self._parameters = list()
        for param in parameters:
            self._parameters.append(JobParameter(param))

    def __str__(self):
        return self._tokenizer.encode(
            self.project.name,
            self.name,
            None)

    def __repr__(self):
        params = dict()
        for param in self.parameters:
            if param.show:
                params[param.name] = param.value

        return self._tokenizer.encode(
            self.project.name,
            self.name,
            params)

    def __eq__(self, value):
        # TODO: better equality
        return str(self) == str(value)

    @property
    def name(self):
        """
        str: Name of the job.
        """
        return self._name

    @property
    def server(self):
        """
        str: String of the server URL.
        """
        return self._server

    @property
    def parameters(self):
        """
        list(:py:class:`kirk.project.JobParameter`): Jenkins job parameters.
        """
        return self._parameters

    @property
    def dependences(self):
        """
        list(str): List of jobs which this job depends to.
        """
        return self._dependences

    @property
    def pipeline(self):
        """
        str: Jenkins job script location.
        """
        return self._pipeline

    @property
    def scm(self):
        """
        dict: Jenkins job scm configuration.
        """
        return self._scm

    @property
    def project(self):
        """
        :py:class:`Project`: Project instance of this job.
        """
        return self._project


class Project:
    """
    Project definition class.
    """

    def __init__(self):
        self._logger = logging.getLogger("project")
        self._name = ""
        self._description = ""
        self._author = ""
        self._year = ""
        self._version = ""
        self._location = ""
        self._jobs = list()

    def load(self, path):
        """
        Load a project configuration.

        Args:
            path(str): configuration file path.

        Raises:
            ValueError: if input args cannot be accepted.
            KirkError: if input file cannot be parsed.
        """
        if not path:
            raise ValueError("'path' is empty")

        # load project file
        self._logger.info("loading file '%s'", path)

        file_def = yaml_env.load(path)

        # validate project file
        self._logger.info("validating file '%s'", path)

        try:
            currdir = os.path.abspath(os.path.dirname(__file__))
            schemafile = os.path.join(currdir, "files", "schema.yml")
            validator = Core(source_data=file_def, schema_files=[schemafile])
            validator.validate(raise_exception=True)
        except PyKwalifyException as err:
            raise KirkError(err)

        # load project informations
        self._name = file_def['name']
        self._description = file_def['description']
        self._author = file_def['author']
        self._year = file_def['year']
        self._version = file_def['version']
        self._location = file_def['location']

        # create jenkins job objects
        self._logger.info("create jobs")

        jobs = file_def['jobs']
        defaults_cfg = file_def['defaults']

        self._jobs.clear()
        for job_cfg in jobs:
            new_job = JobItem(defaults_cfg, job_cfg, self)
            for job in self._jobs:
                if job.name == new_job.name:
                    raise KirkError(
                        "Two jobs with the same name '%s' for project '%s'" %
                        (job.name, self._name))

            self._jobs.append(new_job)

        self._logger.info("project file loaded")

    @property
    def name(self):
        """
        str: Project name.
        """
        return self._name

    @property
    def description(self):
        """
        str: Project description.
        """
        return self._description

    @property
    def author(self):
        """
        str: Project author.
        """
        return self._author

    @property
    def year(self):
        """
        int: Project year.
        """
        return self._year

    @property
    def version(self):
        """
        float: Project version.
        """
        return self._version

    @property
    def location(self):
        """
        float: Project location in the Jenkins server.
        """
        return self._location

    @property
    def jobs(self):
        """
        :py:class:`kirk.project.JobItem`: List of the available jobs.
        """
        return self._jobs
