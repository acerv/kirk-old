"""
.. module:: main
   :platform: Multiplatform
   :synopsis: application entry point
   :license: GPLv2
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import os
import click
import kirk.loader
import kirk.credentials
from kirk.runner import Runner


class Arguments:
    """
    Default program arguments.
    """

    def __init__(self):
        self.credentials = "credentials.cfg"
        self.projects = "projects"
        self.debug = False
        self.rootdir = os.path.abspath(os.path.curdir)


pass_arguments = click.make_pass_decorator(Arguments, ensure=True)


@click.group()
@click.option('--credentials', default="credentials.cfg", help="credentials file")
@click.option('--projects', default="projects", help="projects folder")
@click.option('--debug', is_flag=True, default=False, help="debug mode")
@pass_arguments
def client(args, credentials, projects, debug):
    """
    Kirk - Jenkins remote tester
    """
    # initialize configurations
    args.credentials = credentials
    args.projects = projects
    args.debug = debug

    # start session
    if debug:
        click.secho("debugging session\n", fg="green", bold=True)

    click.echo("session started")
    click.echo("rootdir: %s" % args.rootdir)
    click.echo("credentials: %s, projects: %s" % (credentials, projects))
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
@click.argument("projects", nargs=-1)
def info(args, projects):
    """
    show projects informations
    """
    available_projects, _ = get_available_tests(args)
    if not available_projects:
        return

    all_projects = [proj.name for proj in available_projects]
    not_available = list()
    for proj_in in projects:
        if proj_in not in all_projects:
            not_available.extend(proj_in)

    if not_available:
        click.secho("ERROR: following projects are not available", fg="red")
        for project in not_available:
            click.echo("    %s" % project)
        return

    for project in projects:
        for proj in available_projects:
            if project == proj.name:
                click.secho(proj.name, fg="white", bold=True)
                click.echo("    description: %s" % proj.description)
                click.echo("    author: %s" % proj.author)
                click.echo("    year: %s" % proj.year)
                click.echo("    version: %s" % proj.version)
                click.echo("    location: %s" % proj.location)
                click.echo("    jobs:")

                for job in proj.jobs:
                    click.echo("        %s" % job.name)
                break


@client.command()
@pass_arguments
def show(args):
    """
    list projects and tests inside projects folder
    """
    projects, tests = get_available_tests(args)
    if not projects or not tests:
        return

    click.secho("available projects", fg="white", bold=True)
    for project in projects:
        click.echo("    %s" % project.name)
    click.echo()

    click.secho("available tests", fg="white", bold=True)
    for test in tests:
        click.echo("    %s" % test)


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
@click.option('--user', default=None, help="Jenkins username")
@click.argument("tests", nargs=-1)
def run(args, tests, user):
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
        runner = Runner(args.credentials, projects)
        for test in tests:
            click.secho("-> running %s" % test)

            project, job = test.split("::")
            job_location = runner.run(project, job, user)

            click.secho("-> configured %s" % job_location, fg="green")
    except Exception as err:
        click.secho(str(err), fg="red", err=True)


@client.command()
@pass_arguments
@click.argument("credential", nargs=3)
def credential(args, credential):
    """
    Add a credential inside credentials file.
    """
    url = credential[0]
    user = credential[1]
    password = credential[2]

    click.secho("saving credential:", fg="white", bold=True)
    click.echo("    url:  %s" % url)
    click.echo("    user: %s" % user)
    click.echo()

    kirk.credentials.set_password(
        args.credentials,
        credential[0],
        credential[1],
        credential[2])

    click.secho("credential saved", fg="green")
