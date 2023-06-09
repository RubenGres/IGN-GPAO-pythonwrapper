import dill
import os
import sys

from gpao.builder import Builder
from gpao.project import Project
from gpao.job import Job

CWD = os.getcwd()
PYTHON_KERNEL_PATH = "env.db"

JOBS = {}

def job(**kwargs):
    global JOBS

    session_path = os.path.abspath(PYTHON_KERNEL_PATH)

    def decorator(func):
        name = kwargs.get("name", f"{func.__name__}")
        project = kwargs.get("project", os.path.basename(sys.argv[0]))
        conda_env = kwargs.get("conda_env", None)
        tags = kwargs.get("tags", None)
        args = kwargs.get("args", {})
        deps = kwargs.get("deps", None)
        
        formatted_args = ', '.join(f'{k}={v}' for k, v in args.items())

        python_command = f'"import dill; dill.load_session(\'{session_path}\'); {func.__name__}({formatted_args})"'
        cmd = f"python3 -c {python_command}"
        cmd = cmd.replace('"', '\\"')
        cmd = "cd {CWD} && {cmd}"

        if conda_env:
            cmd = f'conda activate {conda_env} && {cmd}'

        cmd = f'bash -c "{cmd}"'

        if deps:
            job_deps = [JOBS[project][dep] for dep in deps]
        else:
            job_deps = None

        job = Job(name, cmd, tags=tags, deps=job_deps)
        JOBS.setdefault(project, {})[name] = job

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    
    return decorator


def send_jobs(api, projects_names=None):
    global JOBS

    session_path = os.path.abspath(PYTHON_KERNEL_PATH)

    projects_names = projects_names if projects_names else JOBS.keys()

    projects = []
    for name in projects_names:
        project = Project(name, list(JOBS[name].values()))
        projects.append(project)

    builder = Builder(projects)
    dill.dump_session(session_path)
    builder.send_project_to_api(api)

    JOBS = {}