"""
.. module:: main
   :platform: Multiplatform
   :synopsis: application entry point
   :license: GPLv2
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import os
import click
import kirk.utils
from kirk.runner import JobRunner
from kirk.credentials import PlaintextCredentials
from kirk.tokenizer import JobTokenizer


class Arguments:
    """
    Default program arguments.
    """

    def __init__(self):
        self.credentials = "credentials.cfg"
        self.rootdir = os.path.abspath(os.path.curdir)
        self.credentials_hdl = None
        self.runner = None
        self.jobs = None
        self.debug = False


pass_arguments = click.make_pass_decorator(Arguments, ensure=True)


def load_jobs(folder):
    """
    Return the list of the available jobs.
    """
    jobs = None
    try:
        jobs = kirk.utils.get_jobs_from_folder(folder)
        click.secho("collected %d jobs\n" %
                    len(jobs), fg="white", bold=True)
    except Exception as err:
        click.secho("ERROR: %s" % err, fg="red", bold=True, err=True)

    return jobs


def load_projects(jobs):
    """
    Return the list of the available project.
    """
    projects = list()
    for job in jobs:
        if job.project not in projects:
            projects.append(job.project)

    return projects


@click.group()
@click.option('-c', '--credentials', default="credentials.cfg", help="credentials file")
@click.option('-p', '--projects', default="projects", help="projects folder")
@click.option('-d', '--debug', is_flag=True, default=False, help="debug mode")
@click.option('-o', '--owner', required=False, nargs=1, default=False, help="main user")
@pass_arguments
def client(args, credentials, projects, debug, owner):
    """
    Kirk - Jenkins remote tester
    """
    # initialize configurations
    args.jobs = load_jobs(projects)
    args.debug = debug
    args.credentials_hdl = PlaintextCredentials(credentials)
    args.runner = JobRunner(args.credentials_hdl, owner=owner)

    # start session
    if debug:
        click.secho("debugging session\n", fg="green", bold=True)

    click.echo("session started")
    click.echo("rootdir: %s" % args.rootdir)
    click.echo("credentials: %s, projects: %s" % (credentials, projects))
    click.echo()


@client.command()
@pass_arguments
@click.option('-j', '--jobs', is_flag=True, default=False, help="list the available of jobs")
@click.option('-p', '--projects', is_flag=True, default=False, help="list the available projects")
@click.argument("job_repr", required=False, default=None, nargs=1)
def show(args, jobs, projects, job_repr):
    """
    show informations about available projects or jobs

    To show jobs (default behaviour):

        kirk show --jobs

    To show projects:

        kirk show --projects

    """
    if jobs:
        if not args.jobs:
            return

        click.secho("available jobs", fg="white", bold=True)
        for job in args.jobs:
            click.echo("  %s" % str(job))
            if job.parameters:
                for param in job.parameters:
                    click.echo("  - %s" % str(param))
                click.echo()
    elif projects:
        proj_list = load_projects(args.jobs)
        if not proj_list:
            return

        click.secho("available projects", fg="white", bold=True)
        for project in proj_list:
            click.echo("  %s" % project.name)
            for job in project.jobs:
                click.echo("   - %s" % job.name)
            click.echo()


@client.command()
@pass_arguments
@click.argument("testregexp", nargs=1)
def search(args, testregexp):
    """
    search for tests inside project files using regexp

    Usage:

        kirk search .*unittest.*

    """
    projects = load_projects(args.jobs)
    if not projects:
        return

    try:
        found = kirk.utils.get_project_regexp(testregexp, projects)
        if not found:
            click.secho("no tests found.")
        else:
            click.secho("found tests", fg="white", bold=True)
            for job in found:
                click.echo("  %s" % str(job))
    except Exception as err:
        click.secho("ERROR: %s" % str(err), fg="red")


@client.command()
@pass_arguments
@click.option('-u', '--user', default=None, help="Jenkins username")
@click.argument("tests", nargs=-1)
def run(args, tests, user):
    """
    run a list of tests

    Usage, to run as owner:

        kirk run <myproject>::<mytest> ...

    Usage, to run as user:

        kirk run -u <myuser> <myproject>::<mytest> ...

    """
    if not args.jobs:
        return

    # show found tests
    click.secho("selected tests", fg="white", bold=True)
    for test in tests:
        click.echo("  " + test)
    click.echo()

    # get jobs to run
    jobs_to_run = list()
    tokenizer = JobTokenizer()
    for test in tests:
        for job in args.jobs:
            if test != str(job):
                continue

            # we found the job
            jobs_to_run.append(job)

            # update job parameters
            _, _, params = tokenizer.decode(test)
            if not params:
                break

            for key, value in params.items():
                for i in range(0, len(job.parameters)):
                    if job.parameters[i].name == key:
                        job.parameters[i].value = value
                        break

    if len(jobs_to_run) != len(tests):
        click.secho("ERROR: cannot find the following jobs", fg="red")

        not_available = list(tests)
        for job in jobs_to_run:
            not_available.remove(str(job))

        for test in not_available:
            click.echo("  %s" % test)

        click.echo("\nplease use 'show' command to list available tests")
        return

    try:
        # run all tests
        for job in jobs_to_run:
            click.secho("-> running %s" % str(job))
            job_location = args.runner.run(job, user)
            click.secho("-> configured %s" % job_location, fg="green")
    except Exception as err:
        click.secho(str(err), fg="red", err=True)


@client.command()
@pass_arguments
@click.argument("credential", nargs=2)
def credential(args, credential):
    """
    add a new user inside credentials file

    Usage:

        kirk credential <myurl> <myuser>

    """
    url = credential[0]
    user = credential[1]

    click.secho("saving credential:", fg="white", bold=True)
    click.echo("  url:  %s" % url)
    click.echo("  user: %s" % user)

    password = click.prompt("  type your password", hide_input=True)

    args.credentials_hdl.set_password(url, user, password)

    click.echo()
    click.secho("credential saved", fg="green")
