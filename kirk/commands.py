"""
.. module:: main
   :platform: Multiplatform
   :synopsis: application entry point
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import os
import sys
import time
import traceback
import click
import kirk.utils
from kirk import __version__
from kirk import KirkError
from kirk.runner import JobRunner
from kirk.credentials import CredentialsHandler
from kirk.tokenizer import JobTokenizer
from kirk.checker import JenkinsTester


class Arguments:
    """
    Default program arguments.
    """

    def __init__(self):
        self.credentials = "credentials.cfg"
        self.rootdir = os.path.abspath(os.path.curdir)
        self.runner = None
        self.jobs = None
        self.debug = False


pass_arguments = click.make_pass_decorator(Arguments, ensure=True)


def print_error(err, debug):
    """
    Print an error message and close the application calling sys.exit(1).

    Args:
        err(Exception): exception to show.
        debug(bool): if True, this function will print traceback as well as the
            exception message.
    """
    click.secho("%s" % err, fg="red", bold=True, err=True)
    if debug:
        msg = traceback.format_exc()
        click.secho(msg, fg="red", err=True)
    sys.exit(1)


def load_jobs(folder):
    """
    Return the list of the available jobs inside ``folder``.

    Args:
        folder(str): folder where projects are located.

    Returns:
        list(:py:class:`kirk.project.JobItem`): list of jobs fetched from ``folder``.
    """
    jobs = None
    try:
        jobs = kirk.utils.get_jobs_from_folder(folder)
        click.secho("collected %d jobs\n" %
                    len(jobs), fg="green", bold=True)
    except KirkError as err:
        print_error(err, True)
    except ValueError as err:
        print_error(err, False)
    except TypeError as err:
        print_error(err, False)

    return jobs


def load_projects(jobs):
    """
    Return the list of the available projects according to ``jobs``.

    Args:
        jobs(list(:py:class:`kirk.project.JobItem`)): list of jobs.

    Returns:
        list(str): list of projects for all the given ``jobs``.
    """
    projects = list()
    for job in jobs:
        if job.project not in projects:
            projects.append(job.project)

    return projects


@click.group()
@click.option(
    '--credentials',
    '-c',
    default="credentials.cfg",
    type=click.Path(exists=False, readable=True),
    help="File that stores owners credentials (default: credentials.cfg)")
@click.option(
    '--projects',
    '-p',
    default="projects",
    type=click.Path(exists=True, readable=True, dir_okay=True),
    help="Folder containing projects definitions (default: projects)")
@click.option(
    '--debug',
    '-d',
    is_flag=True,
    default=False,
    help="Activate the debug mode for the application (default: False)")
@click.option(
    '--owner',
    '-o',
    required=False,
    nargs=1,
    default='kirk',
    help="Jenkins user that will create and build jobs (default: kirk)")
@pass_arguments
def command_kirk(args, credentials, projects, debug, owner):
    """
    Kirk - Jenkins remote tester.

    This is a tool that can be used to create and run Jenkins jobs, without
    the need to create them by yourself and taking advantage of groovy scripts
    saved inside your project.
    """
    # start session
    if debug:
        click.secho("debugging session\n", fg="green", bold=True)

    click.secho("kirk %s session started\n" %
                __version__, fg="yellow", bold=True)
    click.echo("owner: %s" % owner)
    click.echo("rootdir: %s" % args.rootdir)
    click.echo("projects: %s" % projects)
    click.echo("credentials: %s\n" % credentials)

    # initialize configurations
    args.jobs = load_jobs(projects)
    args.debug = debug

    credentials_hdl = CredentialsHandler(credentials)
    args.runner = JobRunner(credentials_hdl, owner=owner)


@command_kirk.command(name='list')
@pass_arguments
@click.option(
    '-j',
    '--jobs',
    is_flag=True,
    default=False,
    help="List the available jobs")
def show(args, jobs):
    """
    Show informations about available projects and jobs.

    To show jobs only:

        kirk list --jobs

    """
    if jobs:
        if not args.jobs:
            return

        click.secho("available jobs", fg="white", bold=True)
        for job in args.jobs:
            click.echo("  %s" % repr(job))
    else:
        proj_list = load_projects(args.jobs)
        if not proj_list:
            return

        click.secho("available projects", fg="white", bold=True)
        for project in proj_list:
            click.echo("  %s" % project.name)
            for job in project.jobs:
                click.echo("   - %s" % repr(job))
            click.echo()


@command_kirk.command()
@pass_arguments
@click.argument("regexp", nargs=1)
def search(args, regexp):
    """
    Search for available jobs using REGEXP.

    Usage:

        kirk search .*unittest.*

    """
    projects = load_projects(args.jobs)
    if not projects:
        return

    try:
        found = kirk.utils.get_project_regexp(regexp, projects)
        if not found:
            raise KirkError("No jobs found.")
        else:
            click.secho("found jobs", fg="white", bold=True)
            for job in found:
                click.echo("  %s" % repr(job))
    except KirkError as err:
        print_error(err, args.debug)


@command_kirk.command()
@pass_arguments
@click.option(
    '--user',
    '-u',
    default="",
    type=str,
    help="Name of the developer that is running the job (default: None)")
@click.option(
    '--change-id',
    '-c',
    default="",
    type=str,
    help="Source code change identifier. By default latest is used")
@click.argument("jobs_repr", nargs=-1)
def run(args, jobs_repr, user, change_id):
    """
    Run a list of jobs as USER with the specified CHANGE_ID.

    To run jobs as owner:

        kirk run <myproject>::<mytest> ...

    To run jobs as user (it will create a developer folder):

        kirk run -u <myuser> <myproject>::<mytest>

    To run jobs in a specific source code change:

        kirk run  -c <change_id> <myproject>::<mytest>

    """
    if not args.jobs:
        return

    # show found tests
    click.secho("selected jobs", fg="white", bold=True)
    for job_str in jobs_repr:
        click.echo("  " + job_str)
    click.echo()

    try:
        # get jobs to run
        jobs_to_run = dict()
        tokenizer = JobTokenizer()

        for job_str in jobs_repr:
            token = tokenizer.decode(job_str)
            if not token:
                raise KirkError(
                    "Invalid job token. Please use the following syntax:\n"
                    "\n  <project>::<job>[<parameters>]\n"
                )

            project, job_name, params = token

            for job in args.jobs:
                if job_name == job.name and project == job.project.name:
                    # we found the job
                    jobs_to_run[job_str] = job
                    break

            for name, value in params.items():
                for i in range(0, len(job.parameters)):
                    if job.parameters[i].name == name:
                        job.parameters[i].value = value
                        break

        if len(jobs_to_run) != len(jobs_repr):
            err = "Cannot find the following jobs\n"

            not_available = list(jobs_repr)
            for key, value in jobs_to_run.items():
                not_available.remove(key)

            for job_str in not_available:
                err += "  %s\n" % job_str

            err += "\nPlease use 'list' command to show available jobs"
            raise KirkError(err)

        # run all tests
        for job_str, job in jobs_to_run.items():
            click.secho("-> running %s (user='%s')" % (job_str, user))
            job_location = args.runner.run(job, user=user, change_id=change_id)
            click.secho("-> configured %s" % job_location, fg="green")
    except KirkError as err:
        print_error(err, args.debug)


@click.command()
@click.option(
    '-c',
    '--credentials',
    default="credentials.cfg",
    type=click.Path(exists=False, writable=True),
    help="File that stores owners credentials (default: credentials.cfg)")
@click.argument("url", nargs=1, required=True)
@click.argument("user", nargs=1, required=True)
def command_credential(credentials, url, user):
    """
    Add a new credential for USER and the given URL.
    """
    click.secho("saving credential:", fg="white", bold=True)
    click.echo("  url:  %s" % url)
    click.echo("  user: %s" % user)
    token = click.prompt("  password", hide_input=True)

    try:
        handler = CredentialsHandler(credentials)
        handler.set_password(url, user, token)
    except KirkError as err:
        print_error(err, True)

    click.echo()
    click.secho("credential saved", fg="green")


@click.command()
@click.argument("url", nargs=1, required=True)
@click.argument("user", nargs=1, required=True)
@click.argument("token", nargs=1, required=True)
def command_check(url, user, token):
    """
    This tool performs tests to understand if USER is allowed to use kirk,
    as well as the URL is configured properly.
    """
    tester = JenkinsTester(url, user, token)
    tests = {
        'connection test': tester.test_connection,
        'plugins installed': tester.test_plugins,
        'create job': tester.test_job_create,
        'configure job': tester.test_job_config,
        'fetching job info': tester.test_job_info,
        'build job': tester.test_job_build,
        'delete job': tester.test_job_delete,
    }

    click.secho("kirk-check session started\n", fg='yellow', bold=True)
    click.echo("  url: %s" % url)
    click.echo("  user: %s" % user)
    click.echo("  token: *******\n")

    try:
        length = len(tests)
        index = 0

        for msg, test in tests.items():
            index += 1
            click.echo("  %d/%d   %s" % (index, length, msg), nl=False)
            test()
            time.sleep(0.2)
            click.secho("  PASSED", fg="green")
    except KirkError as err:
        click.secho("  FAILED", fg="red")
        print_error(err, True)
