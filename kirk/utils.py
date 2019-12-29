"""
.. module:: loader
   :platform: Multiplatform
   :synopsis: various utilities
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import os
import re
from kirk import KirkError
from kirk.project import Project


def get_projects_from_folder(folder):
    """
    Return projects discovered in the given directory.

    Args:
        folder(str): folder containing projects files.

    Returns:
        list(:py:class:`kirk.project.Project`): list of projects.

    Raises:
        ValueError: raised when folder argument is empty or folder doesn't exist.
        :py:class:`KirkError`: raised when there are two projects with the same name.
    """
    if not folder:
        raise ValueError("folder is empty")

    if not os.path.isdir(folder):
        raise ValueError("project folder doesn't exist")

    projects = list()

    for currfile in os.listdir(folder):
        _, file_ext = os.path.splitext(currfile)
        if file_ext not in ('.yml', '.yaml'):
            continue

        projectfile = folder + "/" + currfile

        project = Project()
        project.load(projectfile)

        for proj in projects:
            if proj.name == project.name:
                raise KirkError("Two projects with the same name")

        projects.append(project)

    return projects


def get_jobs_from_folder(folder):
    """
    Return jobs discovered in the given directory.

    Args:
        folder(str): folder containing projects files.

    Returns:
        list(:py:class:`kirk.project.JobItem`): list of jobs.

    Raises:
        ValueError: raised when folder argument is empty or folder doesn't exist.
        :py:class:`KirkError`: raised when there are two projects with the same name.
    """
    projects = get_projects_from_folder(folder)

    jobs = list()
    for project in projects:
        jobs.extend(project.jobs)

    return jobs


def get_project_regexp(regexp, projects):
    """
    Return projects of which the regexp matches projects name.

    Args:
        regexp(str): regular expression used to match projects names.
        projects(:py:class:`kirk.project.Project`): list of projects.

    Returns:
        list(:py:class:`kirk.project.Project`): list of projects.

    Raises:
        ValueError: raised when input arguments are empty.
    """
    if not regexp:
        raise ValueError("regexp is not defined")

    if not projects:
        raise ValueError("projects are empty")

    matcher = re.compile(regexp)
    found = list()
    for proj in projects:
        for job in proj.jobs:
            if matcher.match(str(job)):
                found.append(job)

    return found
