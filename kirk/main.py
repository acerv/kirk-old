"""
.. module:: main
   :platform: Multiplatform
   :synopsis: application entry point
   :license: GPLv2
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import click
import kirk.loader
from kirk.runner import Runner


# command arguments
_config = "kirk.ini"
_projects = None
_user = "admin"
_password = "admin"
_debug = False


@click.group()
@click.option('--config', type=click.File('r'), default="kirk.ini", help="configuration file")
@click.option('--projects', default="projects", help="projects folder")
@click.option('--user', default="admin", help="Jenkins username")
@click.option('--password', default="admin", help="Jenkins password")
@click.option('--debug', is_flag=True, default=False, help="debug mode")
def client(config, projects, user, password, debug):
    """
    Kirk - Jenkins remote tester
    """
    global _config
    global _projects
    global _user
    global _password
    global _debug

    _config = config
    _projects = projects
    _user = user
    _password = password
    _debug = debug

    click.echo()
    click.echo("Session started:")
    click.echo("- config:\t%s" % config.name)
    click.echo("- projects:\t%s" % projects)
    click.echo("- debug:\t%s" % debug)
    click.echo("- user:\t\t%s" % _user)
    click.echo()

    _projects = kirk.loader.load(projects)


@client.command()
def list():
    """
    list tests inside projects folder
    """
    click.echo("Available tests:")
    for proj in _projects:
        for job in proj.jobs:
            click.echo("\t%s::%s" % (proj.name, job.name))


@client.command()
@click.argument("testregexp", nargs=1)
def search(testregexp):
    """
    search for tests inside project files using regexp
    """
    found = kirk.loader.search(testregexp, _projects)
    if not found:
        click.echo("Tests not found!")
    else:
        click.echo("Found tests:")
        for proj, job in found:
            click.echo("\t%s::%s" % (proj, job))


@client.command()
@click.option("--owner", is_flag=True, default=False, help="run as owner")
@click.argument("testregexp", nargs=-1)
def run(testregexp, owner):
    """
    run a list of tests in the format <project>::<test>
    """
    click.echo("Selected tests:")
    for test in testregexp:
        click.echo("  " + test)
    click.echo("")

    if owner:
        click.echo("Running tests as owner:")
    else:
        click.echo("Running tests as developer:")

    try:
        runner = Runner(_user, _password, _projects)
        for test in testregexp:
            click.echo("-> running %s: " % test, nl=False)
            project, job = test.split("::")

            if owner:
                job_location = runner.run_as_owner(project, job)
            else:
                job_location = runner.run_as_developer(project, job)

            click.echo("%s" % job_location)
    except Exception as err:
        click.echo(err)
