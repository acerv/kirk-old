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

    def encode(self, project, job, params, show_params=True):
        """
        Encode project name, job name and job parameters into a unique
        string identifier.
        :param project: project name
        :type project: str
        :param job: job name
        :type job: str
        :param params: list of parameters with value
        :type params: dict
        :param show_params: if False, parameters will be hided
        :type show_params: bool
        :return: str
        """
        raise NotImplementedError()

    def decode(self, token):
        """
        Decode a token string into project name, job name and job parameters.
        :param token: token string
        :type token: str
        :return: (str, str, list(str))
        """
        raise NotImplementedError()


class JobTokenizer(Tokenizer):
    """
    Tokenizer that encode job string as following:

        project = "myproject"
        job = "myjob"
        params = dict(
            param0="0",
            param1="1",
        )

    becomes...

        "myproject::job[param0=0,param1=1]"

    """

    def __init__(self):
        self._re_pattern = re.compile(
            r"(?P<project>\w+)::(?P<job>\w+)(?P<params>\[(\w+=\w+,?)*\])?"
        )

    def encode(self, project, job, params, show_params=True):
        if not project:
            raise ValueError("project name is empty")

        if not job:
            raise ValueError("job name is empty")

        # convert parameters
        params_arg = list()
        if show_params:
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
