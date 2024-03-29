"""
.. module:: tokenizer
   :platform: Multiplatform
   :synopsis: string -> job and vice-versa convertion
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import re


class Tokenizer:
    """
    A generic string tokenizer.
    """

    def encode(self, project, job, params=None):
        """
        Encode ``project``, ``job`` and ``params`` into a unique string
        identifier.

        Args:
            project(str): project name.
            job(str): job name.
            params(dict): list of parameters with value. If None, they are not
                used by method.

        Returns:
            str: encoded string.
        """
        raise NotImplementedError()

    def decode(self, token):
        """
        Decode a token string into project name, job name and job parameters.

        Args:
            token(str): token string that identifies a job.

        Returns:
            (str, str, dict): a set cotaining project name, job name, dict of parameters.
        """
        raise NotImplementedError()


class JobTokenizer(Tokenizer):
    """
    A job tokenizer. The following data:

    .. code-block:: python

        project = "myproject"
        job = "myjob"
        params = dict(
            param0="0",
            param1="1",
        )

    will become...

    .. code-block:: python

        "myproject::job[param0=0,param1=1]"

    """

    def __init__(self):
        self._re_pattern = re.compile(
            r"(?P<project>\w+)::(?P<job>\w+)(?P<params>\[(\w+=\w+,?)*\])?"
        )

    def encode(self, project, job, params=None):
        if not project:
            raise ValueError("project name is empty")

        if not job:
            raise ValueError("job name is empty")

        # convert parameters
        params_arg = list()
        if params:
            for key, value in params.items():
                arg = "%s=%s" % (key, value)
                params_arg.append(arg)

        # convert string
        encoded = "%s::%s" % (project, job)
        if params_arg:
            arg = ",".join(params_arg)
            encoded += "[%s]" % arg

        return encoded

    def decode(self, token):
        if not token:
            raise ValueError("token is empty")

        # remove whitespaces
        my_token = token.replace(" ", "")

        # match for project::job[param0=0,param1=1]
        match = self._re_pattern.match(my_token)
        if not match:
            return None

        # get project and job name
        project = match.group('project')
        job = match.group('job')

        # get parameters
        params = dict()

        match_params = match.group('params')
        if match_params:
            params_list = re.findall(r"(\w+=\w+)", match_params)

            for param in params_list:
                args = param.split("=")
                params[args[0]] = args[1]

        return project, job, params
