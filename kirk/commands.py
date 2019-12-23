"""
.. module:: main
   :platform: Multiplatform
   :synopsis: application entry point
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import os
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
    Print an error message
    """
    click.secho("%s" % err, fg="red", bold=True, err=True)
    if debug:
        msg = traceback.format_exc()
        click.secho(msg, fg="red", err=True)


def load_jobs(folder):
    """
    Return the list of the available jobs.
    """
    jobs = None
    try:
        jobs = kirk.utils.get_jobs_from_folder(folder)
        click.secho("collected %d jobs\n" %
                    len(jobs), fg="green", bold=True)
    except Exception as err:
        print_error(err, True)

    return jobs


def load_projects(jobs):
    """
    Return the list of the available projects.
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
@click.option('-o', '--owner', required=False, nargs=1, default='kirk', help="main user")
@pass_arguments
def command_kirk(args, credentials, projects, debug, owner):
    """
    Kirk - Jenkins remote tester
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
@click.option('-j', '--jobs', is_flag=True, default=False, help="list the available of jobs")
@click.argument("job_repr", required=False, default=None, nargs=1)
def show(args, jobs, job_repr):
    """
    show informations about available projects or jobs

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
    search for jobs inside project files using regexp

    Usage:

        kirk search .*unittest.*

    """
    projects = load_projects(args.jobs)
    if not projects:
        return

    try:
        found = kirk.utils.get_project_regexp(regexp, projects)
        if not found:
            click.secho("no jobs found.")
        else:
            click.secho("found jobs", fg="white", bold=True)
            for job in found:
                click.echo("  %s" % repr(job))
    except Exception as err:
        print_error(err, args.debug)


@command_kirk.command()
@pass_arguments
@click.option('-u', '--user', default="", type=str, help="Jenkins username")
@click.argument("jobs_repr", nargs=-1)
def run(args, jobs_repr, user):
    """
    run a list of jobs

    Usage, to run as owner:

        kirk run <myproject>::<mytest> ...

    Usage, to run as user (it will create a developer folder):

        kirk run -u <myuser> <myproject>::<mytest> ...

    """
    if not args.jobs:
        return

    # show found tests
    click.secho("selected jobs", fg="white", bold=True)
    for job_str in jobs_repr:
        click.echo("  " + job_str)
    click.echo()

    # get jobs to run
    jobs_to_run = dict()
    tokenizer = JobTokenizer()

    for job_str in jobs_repr:
        _, job_name, params = tokenizer.decode(job_str)

        for job in args.jobs:
            if job_name == job.name:
                # we found the job
                jobs_to_run[job_str] = job
                break

        for name, value in params.items():
            for i in range(0, len(job.parameters)):
                if job.parameters[i].name == name:
                    job.parameters[i].value = value
                    break

    if len(jobs_to_run) != len(jobs_repr):
        click.secho("ERROR: cannot find the following jobs", fg="red")

        not_available = list(jobs_repr)
        for key, value in jobs_to_run.items():
            not_available.remove(key)

        for job_str in not_available:
            click.echo("  %s" % job_str)

        click.echo("\nplease use 'list' command to show available jobs")
        return

    try:
        # run all tests
        for job_str, job in jobs_to_run.items():
            click.secho("-> running %s (user='%s')" % (job_str, user))
            job_location = args.runner.run(job, user)
            click.secho("-> configured %s" % job_location, fg="green")
    except Exception as err:
        print_error(err, args.debug)


@click.command()
@click.argument("args", nargs=2)
@click.option('-c', '--credentials', default="credentials.cfg", help="credentials file location")
def command_credential(args, credentials):
    """
    Add new credentials inside the credentials file.

    Usage:

        kirk-credential <url> <user>

    """
    url = args[0]
    user = args[1]

    click.secho("saving credential:", fg="white", bold=True)
    click.echo("  url:  %s" % url)
    click.echo("  user: %s" % user)
    token = click.prompt("  password", hide_input=True)

    try:
        handler = CredentialsHandler(credentials)
        handler.set_password(url, user, token)
    except Exception as err:
        print_error(err, True)

    click.echo()
    click.secho("credential saved", fg="green")


@click.command()
@click.argument("args", nargs=3)
def command_check(args):
    """
    Checks if requisites to run kirk are satisfied.
    Usage:

        kirk-check <url> <user> <token>

    """
    url = args[0]
    user = args[1]
    password = args[2]

    tester = JenkinsTester(url, user, password)
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
    click.echo("  password: *******\n")

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
