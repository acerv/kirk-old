"""
.. module:: loader
   :platform: Multiplatform
   :synopsis: module containing project loaders
   :license: GPLv2
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import re
import os
import logging
from kirk import KirkError
from kirk.config import Project


_logger = logging.getLogger("main")


def load(folder):
    """
    Load all projects from the given directory.
    :param folder: directory where projects files are located
    :type folder: str
    :return: list(Project)
    """
    if not folder:
        raise ValueError("folder")

    projects = list()

    for currfile in os.listdir(folder):
        _, file_ext = os.path.splitext(currfile)
        if file_ext not in ('.yml', '.yaml'):
            continue

        # load project file
        projectfile = folder + "/" + currfile

        _logger.info("loading '%s'", projectfile)
        project = Project()
        project.load(projectfile)

        _logger.info("checking for name conflicts")
        for proj in projects:
            if proj.name == project.name:
                raise KirkError("Two projects with the same name")

        projects.append(project)

        _logger.info("project loaded")

    return projects


def search(regexp, projects):
    """
    Search for tests inside projects using regular expressions.
    :param regexp: regexp to use for all tests names
    :type regexp: str
    :param projects: projects to search into
    :type projects: list(Project)
    :return: list of tuple like (<project>, <job>)
    """
    _logger.info("searching for tests matching '%s'", regexp)

    found = list()
    for proj in projects:
        for job in proj.jobs:
            if re.match(regexp, job.name):
                found.append((proj.name, job.name))
                _logger.info("found job into project '%s'", proj.name)

    return found
