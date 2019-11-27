"""
.. module:: main
   :platform: Multiplatform
   :synopsis: application entry point
   :license: GPLv2
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import argparse
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

import kirk.loader
from kirk.runner import Runner


def _cmd():
    """
    Entry point for setuptools.
    """
    # pylint: disable=invalid-name
    _parser = argparse.ArgumentParser(
        description="Kirk - Jenkins remote tester")
    _parser.add_argument(
        "-c",
        "--config",
        default="kirk.ini",
        help="configuration file")
    _parser.add_argument(
        "-p",
        "--projects",
        default="projects",
        help="projects folder")
    _parser.add_argument(
        "-u",
        "--user",
        default="admin",
        help="override jenkins username inside configuration")
    _parser.add_argument(
        "-t",
        "--token",
        default="",
        help="override jenkins user token inside configuration")
    _parser.add_argument(
        "-s",
        "--search",
        help="search for tests inside project files using regexp")
    _parser.add_argument(
        "-l",
        "--list",
        action='store_true',
        help="show all projects")
    _parser.add_argument(
        "-r",
        "--run",
        nargs='*',
        help="list of tests to run")

    _arguments = _parser.parse_args()

    # load projects
    print("Loading projects files...")
    projects = kirk.loader.load(_arguments.projects)

    # if search is defined, search test inside the projects list
    if _arguments.search:
        found = kirk.loader.search(_arguments.search, projects)
        for proj, job in found:
            print("%s::%s" % (proj, job))
    elif _arguments.list:
        for proj in projects:
            for job in proj.jobs:
                print("%s::%s" % (proj.name, job.name))
    elif _arguments.run:
        runner = Runner(_arguments.user, _arguments.token, projects)
        print("Selected tests:")
        for test in _arguments.run:
            print(" - " + test)
        print("\n")

        try:
            for test in _arguments.run:
                print("Running test %s..." % test)
                project, job = test.split("::")
                runner.run_as_developer(project, job)
                print("done!")
        except Exception as err:
            print(err)


def _open_ui():
    """
    Entry point for main form.
    """
    raise NotImplementedError("Not implemented yet")
