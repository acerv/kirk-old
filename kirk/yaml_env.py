"""
.. module:: yaml_env
   :platform: Multiplatform
   :synopsis: Yaml files loader with environment variables support
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import re
import os
import yaml
from kirk import KirkError


def _yaml_constructor(loader, node):
    """
    Get environment variables.
    """
    pattern = re.compile(r'.*?\${(\w+)}.*?')
    value = loader.construct_scalar(node)
    match = pattern.findall(value)  # to find all env variables in line
    if match:
        full_value = value
        for item in match:
            full_value = full_value.replace(
                f'${{{item}}}', os.environ.get(item, item)
            )
        return full_value
    return value


def load(path, tag="!ENV"):
    """
    Load an extended yaml file with environmental variables support.
    For example

    .. code-block:: yaml

        name: !ENV ${MY_ENV_VAR}

    Args:
        path(str): path of the Yaml file.
        tag(str): environment variable tag (default: '!ENV').

    Returns:
        dict: file content.
    """
    if not path:
        raise ValueError("path is empty")

    if not tag:
        raise ValueError("tag is empty")

    if not os.path.isfile(path):
        raise ValueError("'%s' file doesn't exist" % path)

    # check for project file extension
    _, file_ext = os.path.splitext(path)
    if file_ext not in ('.yml', '.yaml'):
        raise KirkError("'%s' file type is not supported" % file_ext)

    # check for environment tags
    imp_pattern = re.compile(r'%s .*?\${(\w+)}.*?' % tag)

    yaml.SafeLoader.add_implicit_resolver(tag, imp_pattern, None)
    yaml.SafeLoader.add_constructor(tag, _yaml_constructor)

    # load project file
    file_def = dict()
    with open(path, 'r') as stream:
        file_def = yaml.load(stream, Loader=yaml.SafeLoader)

    return file_def
