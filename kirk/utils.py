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
    Return all projects discovered in the given directory.
    :param folder: directory where projects files are located
    :type folder: str
    :return: list(Project)
    """
    if not folder:
        raise ValueError("folder is empty")

    if not os.path.isdir(folder):
        raise ValueError("folder is not a directory")

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
    Return all jobs discovered in the given directory.
    :param folder: directory where projects files are located
    :type folder: str
    :return: list(str)
    """
    projects = get_projects_from_folder(folder)

    jobs = list()
    for project in projects:
        jobs.extend(project.jobs)

    return jobs


def get_project_regexp(regexp, projects):
    """
    Search for tests inside a projects list using regular expressions.
    :param regexp: regexp to use for all tests names
    :type regexp: str
    :param projects: projects to search into
    :type projects: list(Project)
    :return: list(JobItem)
    """
    if not regexp:
        raise ValueError("regexp is not defined")

    if not projects:
        raise ValueError("projects are empty")

    found = list()
    for proj in projects:
        for job in proj.jobs:
            if re.match(regexp, str(job)):
                found.append(job)

    return found
