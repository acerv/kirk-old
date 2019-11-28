"""
.. module:: main
   :platform: Multiplatform
   :synopsis: application entry point
   :license: GPLv2
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import os
import configparser
import click
import kirk.loader
from kirk.runner import Runner


class Arguments:
    """
    Default program arguments.
    """

    def __init__(self):
        self.config = "kirk.ini"
        self.projects = "projects"
        self.username = "admin"
        self.password = "admin"
        self.debug = False
        self.rootdir = os.path.abspath(os.path.curdir)


pass_arguments = click.make_pass_decorator(Arguments, ensure=True)


@click.group()
@click.option('--config', default="kirk.ini", help="configuration file")
@click.option('--projects', default="projects", help="projects folder")
@click.option('--username', default="admin", help="Jenkins username")
@click.option('--password', default="admin", help="Jenkins password")
@click.option('--debug', is_flag=True, default=False, help="debug mode")
@pass_arguments
def client(args, config, projects, username, password, debug):
    """
    Kirk - Jenkins remote tester
    """
    args.config = config
    args.projects = projects
    args.username = username
    args.password = password
    args.debug = debug

    inifile = None

    if os.path.isfile(config):
        inifile = configparser.ConfigParser()
        inifile.read(config)

        args.username = inifile['kirk']['username']
        args.password = inifile['kirk']['password']

    if username != "admin":
        args.username = username

    if password != "admin":
        args.password = password

    if debug:
        click.secho("debugging session\n", fg="green", bold=True)

    click.echo("session started by '%s'" % username)
    click.echo("rootdir: %s" % args.rootdir)
    click.echo("config: %s, projects: %s" % (config, projects))
    click.echo()


def load_projects(args):
    """
    Return the list of the available projects.
    """
    if not os.path.isdir(args.projects):
        click.secho("ERROR: projects folder doesn't exist",
                    fg="red", bold=True, err=True)
        return None

    projects = None
    try:
        projects = kirk.loader.load(args.projects)
        click.secho("collected %d items\n" %
                    len(projects), fg="white", bold=True)
    except Exception as err:
        click.secho("ERROR: %s" % err, fg="red", bold=True, err=True)

    return projects


def get_available_tests(args):
    """
    Return projects and the list of available tests.
    """
    projects = load_projects(args)
    if not projects:
        return None, None

    tests = list()
    for proj in projects:
        for job in proj.jobs:
            tests.append("%s::%s" % (proj.name, job.name))
    return projects, tests


@client.command()
@pass_arguments
def show(args):
    """
    list tests inside projects folder
    """
    projects, tests = get_available_tests(args)
    if not projects or not tests:
        return

    click.secho("available tests", fg="white", bold=True)
    for test in tests:
        click.secho("    %s" % test)


@client.command()
@pass_arguments
@click.argument("testregexp", nargs=1)
def search(args, testregexp):
    """
    search for tests inside project files using regexp
    """
    projects, tests = get_available_tests(args)
    if not projects or not tests:
        return

    found = kirk.loader.search(testregexp, projects)
    if not found:
        click.secho("no tests found.")
    else:
        click.secho("found tests", fg="white", bold=True)
        for proj, job in found:
            click.echo("    %s::%s" % (proj, job))


@client.command()
@pass_arguments
@click.option("--owner", is_flag=True, default=False, help="run as owner")
@click.argument("tests", nargs=-1)
def run(args, tests, owner):
    """
    run a list of tests in the format <project>::<test>
    """
    projects, all_tests = get_available_tests(args)
    if not projects or not all_tests:
        return

    not_available = list()
    for test in tests:
        if test not in all_tests:
            not_available.append(test)

    if not_available:
        click.secho("ERROR: following tests are not available", fg="red")
        for test in not_available:
            click.echo("    %s" % test)

        click.echo("\nplease use 'show' command to list available tests")
        return

    # show found tests
    click.secho("selected tests", fg="white", bold=True)
    for test in tests:
        click.echo("  " + test)
    click.echo()

    # run all tests
    try:
        runner = Runner(args.username, args.password, projects)
        for test in tests:
            click.secho("-> running %s" % test)

            project, job = test.split("::")

            if owner:
                job_location = runner.run_as_owner(project, job)
            else:
                job_location = runner.run_as_developer(project, job)

            click.secho("-> configured %s" % job_location, fg="green")
    except Exception as err:
        click.secho(err, fg="red", err=True)
